import csv
import datetime
import sys

from colonialismdb.population.models import Location, MainDataEntry

def get_or_add_location(place_name, in1 = None, in2 = None, in3 = None):
  place_name = place_name.title()
  try:
    return Location.objects.get(name__exact = place_name)
  except Location.MultipleObjectsReturned:
    raise # TODO
  except Location.DoesNotExist:
    pass

  prev_loc = None

  for in_loc_name in (in3.title(), in2.title(), in1.title()):
    if not in_loc_name:
      continue

    try:
      prev_loc = Location.objects.get(name__exact = in_loc_name)
    except Location.MultipleObjectsReturned:
      raise # TODO
    except Location.DoesNotExist:
      prev_loc = Location(name = in_loc_name, in_location = prev_loc)
      prev_loc.save()

  prev_loc = Location(name = place_name, in_location = prev_loc)
  prev_loc.save()

  return prev_loc


infile = sys.argv[1]
reader = csv.reader(open(infile, "r"), delimiter=',', quotechar = '"')

for i, row in enumerate(reader):
  rdict = dict(zip(('begin_date', 'end_date', 'place_origin', 'place_english', 'alternate_location_name', 'large1', 'large2', 'large3', 'religion', 'race', 'ethnicity', 'ethnic_origin', 'age_start', 'age_end', 'remarks', 'link', 'individuals_population_value', 'families_population_value', 'male_population_value', 'female_population_value', 'value_unit', 'is_total', 'population_condition', 'polity', 'iso', 'wb'), row[2:]))
  rdict['source_id'] = row[0]

  #if rdict['place_english'] or rdict['alternate_location_name'] : 
  #  print i, rdict['place_origin'], ", ", rdict['alternate_location_name'], ", ", rdict['place_english']

  #continue 

  print i, rdict['place_origin'], ", ", rdict['large1'], ", ", rdict['large2'], ", ", rdict['large3']

  location = get_or_add_location(rdict['place_origin'], rdict['large1'], rdict['large2'], rdict['large3'])

  import pdb; pdb.set_trace()

  del rdict['place_origin']
  del rdict['large1']
  del rdict['large2']
  del rdict['large3']
  del rdict['link']
  del rdict['place_english']
  
  for k in rdict.keys():
    if not rdict[k]:
      del rdict[k]

  if rdict['population_condition'] == 'Neither':
    del rdict['population_condition']

  rdict['remarks'] = rdict['remarks'].decode('ISO-8859-1')

  if rdict['begin_date']:
    mon, day, year = [int(i) for i in rdict['begin_date'].split('/')]
    rdict['begin_date'] = datetime.date(year, mon, day)

  if rdict['end_date']:
    mon, day, year = [int(i) for i in rdict['end_date'].split('/')]
    rdict['end_date'] = datetime.date(year, mon, day)

  rdict['location'] = location

  entry = MainDataEntry(**rdict)
  entry.save()
