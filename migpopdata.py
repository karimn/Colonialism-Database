#!/usr/bin/python

import csv
import datetime
import sys
import re

from colonialismdb.population.models import MainDataEntry, PopulationCondition
from colonialismdb.common.models import Location, Religion, Ethnicity, EthnicOrigin, Race
from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from reversion import revision

mig_user = User.objects.get(username = 'karim')

class LocationTooComplicated(Exception):
  def __init__(self, problem):
    self.problem = problem

  def __str__(self):
    return self.problem

def get_or_add_religion(religion):
  religion = religion.title()

  try:
    return Religion.objects.get(name = religion)
  except Religion.DoesNotExist:
    new_rel = Religion(name = religion, active = True, submitted_by = mig_user)
    new_rel.save()
    return new_rel

def get_or_add_race(race):
  race = race.title()

  try:
    return Race.objects.get(name = race)
  except Race.DoesNotExist:
    new_race = Race(name = race, active = True, submitted_by = mig_user)
    new_race.save()
    return new_race

def get_or_add_ethnicity(eth):
  eth = eth.title()

  try:
    return Ethnicity.objects.get(name = eth)
  except Ethnicity.DoesNotExist:
    new_eth = Ethnicity(name = eth, active = True, submitted_by = mig_user) #, log = default_log)
    new_eth.save()
    return new_eth

def get_or_add_ethnic_origin(eth):
  eth = eth.title()

  try:
    return EthnicOrigin.objects.get(name = eth)
  except EthnicOrigin.DoesNotExist:
    new_eth = EthnicOrigin(name = eth, active = True, submitted_by = mig_user) #, log = default_log)
    new_eth.save()
    return new_eth
  
def get_or_add_pop_cond(cond):
  cond = cond.title()

  try:
    return PopulationCondition.objects.get(name = cond)
  except PopulationCondition.DoesNotExist:
    new_cond = PopulationCondition(name = cond, active = True, submitted_by = mig_user) #, log = default_log)
    new_cond.save()
    return new_cond

def get_or_add_location(place_name, in1 = None, in2 = None, in3 = None):
  place_name = place_name.title()
  prev_loc = None
  prev_tree = Location.objects.all()
  location_created = False

  for in_loc_name in (in3.title(), in2.title(), in1.title()):
    if not in_loc_name:
      continue

    try:
      loc = prev_tree.get(name__exact = in_loc_name)
    except Location.MultipleObjectsReturned:
      loc = None

      if prev_loc:
        immediate_subloc_tree = prev_loc.get_sub_locations(include_self = False, max_distance = 1)

        if immediate_subloc_tree.filter(name__exact = in_loc_name).count() == 1:
          loc = immediate_subloc_tree.get(name__exact = in_loc_name)

      if not loc:
        raise LocationTooComplicated('Found multiple matches for parent location %s' % in_loc_name)
    except Location.DoesNotExist:
      loc = Location(name = in_loc_name, in_location = prev_loc, active = True, submitted_by = mig_user) #, log = default_log)
      loc.save()
      location_created = True
    else:
      if location_created and not prev_loc.is_root():
        raise LocationTooComplicated('Found existing location after having created a non-existent one')
      else:
        loc.in_location = prev_loc

    prev_loc = loc
    prev_tree = prev_loc.get_sub_locations(include_self = False)

  retrying = False
  places = prev_tree.filter(name__exact = place_name)

  while True:
    if len(places) == 1:
      return places[0]

    elif len(places) == 0:
      new_loc = Location(name = place_name, in_location = prev_loc, active = True, submitted_by = mig_user) #, log = default_log)
      new_loc.save()

      return new_loc

    else:
      if retrying:
        raise LocationTooComplicated('Found multiple location matches for requested place')

      if prev_loc:
        places = prev_tree.filter(name__exact = place_name, in_location = prev_loc.pk)
      else:
        places = []
        
      retrying = True
    

# Script begins ###############################################################################                                                       

infile = sys.argv[1]
reader = csv.reader(open(infile, "r"), delimiter='\t', quotechar = '"')

string_encoding = 'ISO-8859-1'

num_err_rows = 0

for i, row in enumerate(reader):
  rdict = dict(zip(('source_id', 'combined_id', 'begin_date', 'end_date', 'place_origin', 'place_english', 'alternate_location_name', 'large1', 'large2', 'large3', 'religion', 'race', 'ethnicity', 'ethnic_origin', 'age_start', 'age_end', 'remarks', 'link', 'individuals_population_value', 'families_population_value', 'male_population_value', 'female_population_value', 'value_unit', 'is_total', 'population_condition', 'polity', 'iso', 'wb'), row))

  #if rdict['place_english'] or rdict['alternate_location_name'] : 
  #  print i, rdict['place_origin'], ", ", rdict['alternate_location_name'], ", ", rdict['place_english']
  #continue 

  #if i < 57600: continue

  val_specified = False

  if not rdict['individuals_population_value'] and rdict['individuals_population_value'] != 0:
    val_specified = True
    rdict['individ_fam'] = 0
    rdict['population_value'] = rdict['individuals_population_value']

  del rdict['individuals_population_value']

  if not rdict['families_population_value'] and rdict['families_population_value'] != 0:
    if val_specified:
      sys.stderr.write('multiple population values in row (%i)\n' % i)
      sys.stderr.write('%s\n' % rdict)
      num_err_rows += 1
      continue

    val_specified = True
    rdict['individ_fam'] = 1
    rdict['population_value'] = rdict['families_population_value']

  del rdict['families_population_value']

  if not rdict['male_population_value'] and rdict['male_population_value'] != 0:
    if val_specified:
      sys.stderr.write('multiple population values in row (%i)\n' % i)
      sys.stderr.write('%s\n' % rdict)
      num_err_rows += 1
      continue

    val_specified = True
    rdict['individ_fam'] = 0
    rdict['population_value'] = rdict['male_population_value']
    rdict['population_gender'] = 'm'

  del rdict['male_population_value']

  if not rdict['female_population_value'] and rdict['female_population_value'] != 0:
    if val_specified:
      sys.stderr.write('multiple population values in row (%i)\n' % i)
      sys.stderr.write('%s\n' % rdict)
      num_err_rows += 1
      continue

    val_specified = True
    rdict['individ_fam'] = 0
    rdict['population_value'] = rdict['female_population_value']
    rdict['population_gender'] = 'f'

  del rdict['female_population_value']

  if not val_specified:
    sys.stderr.write('Data entry with no data in row (%i)\n' % i)
    sys.stderr.write('%s\n' % rdict)
    num_err_rows += 1
    continue

  print i, rdict['place_origin'].decode(string_encoding), u", ", rdict['large1'].decode(string_encoding), u", ", rdict['large2'].decode(string_encoding), u", ", rdict['large3'].decode(string_encoding)

  try:
    rdict['location'] = get_or_add_location(unicode(rdict['place_origin'], string_encoding), unicode(rdict['large1'], string_encoding), unicode(rdict['large2'], string_encoding), unicode(rdict['large3'], string_encoding))
  except DatabaseError as e:
    sys.stderr.write('Database error on getting or adding location in row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    num_err_rows += 1
    continue
  except LocationTooComplicated as e:
    sys.stderr.write('Location too complicated in row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    num_err_rows += 1
    continue

  #import pdb; pdb.set_trace()

  del rdict['place_origin']
  del rdict['large1']
  del rdict['large2']
  del rdict['large3']
  del rdict['link']
  del rdict['place_english']
  
  for k in rdict.keys():
    if not rdict[k]:
      del rdict[k]

  for col_name, add_fun in { 'religion' : get_or_add_religion, 'race' : get_or_add_race, 'ethnicity' : get_or_add_ethnicity, 'ethnic_origin' : get_or_add_ethnic_origin, 'population_condition' : get_or_add_pop_cond }.iteritems():
    if rdict.has_key(col_name):
      try:
        rdict[col_name] = add_fun(rdict[col_name])
      except DatabaseError as e:
        sys.stderr.write("Error on get_or_add_%s in row (%i): %s\n" % (col_name, i, e))
        sys.stderr.write("%s\n" % rdict)
        num_err_rows += 1

  if rdict.has_key('remarks'):
    rdict['remarks'] = rdict['remarks'].decode(string_encoding)

  if rdict.has_key('alternate_location_name'):
    rdict['alternate_location_name'] = rdict['alternate_location_name'].decode(string_encoding)

  try:
    if rdict.has_key('begin_date'):
      mon, day, year = [int(j) for j in rdict['begin_date'].split('/')]
      rdict['begin_date'] = datetime.date(year, mon, day)

    if rdict.has_key('end_date'):
      mon, day, year = [int(j) for j in rdict['end_date'].split('/')]
      rdict['end_date'] = datetime.date(year, mon, day)

  except ValueError as e:
    sys.stderr.write('Encountered error in date format at row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    num_err_rows += 1
    continue

  for age_col in ('age_start', 'age_end'):
    if rdict.has_key(age_col):
      if rdict[age_col] == 'Unknown':
        del rdict[age_col]
      else:
        over_match = re.match(r'Over\s(\d+)', rdict[age_col])
        if over_match:
          del rdict['age_end']
          rdict['age_start'] = over_match.group(1) 

  rdict['active'] = True
  rdict['submitted_by'] = mig_user 
          
  try:
    entry = MainDataEntry(**rdict)
    entry.save()
  except (ValueError, DatabaseError, ValidationError) as e:
    sys.stderr.write('Failed to save data row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    num_err_rows += 1

print 'Migration complete. %i row errors encountered and ignored' % num_err_rows
