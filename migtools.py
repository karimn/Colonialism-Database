from colonialismdb.common.models import Location

def get_or_add_cat_item(item, mig_user, cat):
  if not item or len(item) == 0:
    return None

  item = item.title()

  try:
    return cat.objects.get(name = item)
  except cat.DoesNotExist:
    new_obj = cat(name = item, active = True, submitted_by = mig_user)
    new_obj.save()
    return new_obj

class LocationTooComplicated(Exception):
  def __init__(self, problem):
    self.problem = problem

  def __str__(self):
    return self.problem
  
def get_or_add_location(place_name, mig_user, in1 = None, in2 = None, in3 = None):
  place_name = place_name.title()
  prev_loc = None
  prev_tree = Location.objects.all()
  location_created = False

  for in_loc_name in (in3, in2, in1):
    if not in_loc_name:
      continue

    in_loc_name = in_loc_name.title()

    found_loc = prev_tree.filter(name__exact = in_loc_name)
    found_loc_count = found_loc.count()

    if found_loc_count > 1:
      loc = None

      if prev_loc:
        immediate_subloc_tree = prev_loc.get_geographic_sub_locations(include_self = False, max_distance = 1)

        immed_found_loc = immediate_subloc_tree.filter(name__exact = in_loc_name)
        if immed_found_loc.count() > 0: # Just taking the first match no matter what for now
          loc = immed_found_loc[0] 

      if not loc:
        loc = found_loc[0] # Taking the first match for now
    elif found_loc_count == 0:
      loc = Location(name = in_loc_name, geographically_in = prev_loc, active = True, submitted_by = mig_user) #, log = default_log)
      loc.save()
      location_created = True
    else:
      loc = found_loc[0]
      if location_created and not prev_loc.is_root():
        raise LocationTooComplicated('Found existing location after having created a non-existent one')
      else:
        loc.in_location = prev_loc

    prev_loc = loc
    prev_tree = prev_loc.get_geographic_sub_locations(include_self = False)

  retrying = False
  places = prev_tree.filter(name__exact = place_name)

  while True:
    if len(places) == 1:
      return places[0]

    elif len(places) == 0:
      new_loc = Location(name = place_name, geographically_in = prev_loc, active = True, submitted_by = mig_user) #, log = default_log)
      new_loc.save()

      return new_loc

    else:
      if retrying:
        raise LocationTooComplicated('Found multiple location matches for requested place')

      if prev_loc:
        places = prev_tree.filter(name__exact = place_name, geographically_in = prev_loc.pk)
      else:
        places = []
        
      retrying = True
