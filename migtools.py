import re
import os
import sys

from colonialismdb.common.models import Location
from django.core.files import File
import colonialismdb

#STRING_ENCODING = 'ISO-8859-1'
STRING_ENCODING = 'utf-8'

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

def get_source_file_path(rdict, i, num_err_rows):
  source_file_path = None 
  
  local_path_match = re.match(r'^#?(e:\\[^#]+)', rdict['source_file'], flags = re.IGNORECASE)

  if local_path_match:     
    source_file_path = local_path_match.group(1)
  else:
    peanut_match = re.match(r'#?\\\\peanut\.bu\.edu\\e\\([^#]+)', rdict['source_file'], flags = re.IGNORECASE)

    if peanut_match:
      source_file_path = "e:\\%s" % peanut_match.group(1)
    else:
      relative_path_match = re.match(r'#?(?:\.\.\\){1,2}subproject_([^\\]+)\\([^#]+)', rdict['source_file'], flags = re.IGNORECASE)

      if relative_path_match:
        subproj_dir = relative_path_match.group(1).lower()

        if subproj_dir == 'colonialism':
          source_file_path = 'e:\\colonialism\\project_thebase\\subproject_colonialism\\%s' % relative_path_match.group(2).lower()
        #elif subproj_dir == 'datalabel':
        #  source_file_path = 'e:\\colonialism\\project_thebase\\subproject_colonialism\\%s' % relative_path_match.group(1).lower()
        else:
          sys.stderr.write('Failed to match relative source file path in row (%i)\n' % (i,))
          sys.stderr.write('%s\n' % rdict)
          return None, num_err_rows + 1
      else:
        sys.stderr.write('Failed to match source file path in row (%i)\n' % (i,))
        sys.stderr.write('%s\n' % rdict)
        return None, num_err_rows + 1

  return source_file_path, num_err_rows

def add_source_files(source_file_path, src_obj, submitted_by):
  if os.path.isfile(source_file_path):
    source_file = File(open(source_file_path, 'r'))
    src_file = colonialismdb.sources.models.SourceFile(source_file = source_file, for_source = src_obj, active = True, submitted_by = submitted_by)
    src_file.save()
  elif os.path.isdir(source_file_path):
    for f in os.listdir(source_file_path):
      sub_source_file = "%s/%s" % (source_file_path, f)
      if os.path.isfile(sub_source_file):
        add_source_files(sub_source_file, src_obj, submitted_by)
  else:
    return False
  
  return True
