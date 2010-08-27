#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

from colonialismdb.population.models import MainDataEntry, PopulationCondition
from colonialismdb.common.models import Location, Religion, Ethnicity, EthnicOrigin, Race
from colonialismdb.sources.models import Source, Table
from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from reversion import revision

mig_user = User.objects.get(username = 'karim')
 
get_or_add_religion = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = Religion)
get_or_add_race = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = Race)
get_or_add_ethnicity = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = Ethnicity)
get_or_add_ethnic_origin = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = EthnicOrigin)
get_or_add_pop_cond = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = PopulationCondition)

#get_or_add_location = functools.partial(migtools.get_or_add_location, mig_user = mig_user)

def add_row(rdict, num_err_rows):
  if rdict['old_combined_id']:
    cid_matches = re.match(r'([^\.-]+)[\.-]([^\.-]+)', rdict['old_combined_id'])

    if not cid_matches:
      sys.stderr.write('Failed to match combined id %s in row (%i)\n' % (rdict['old_combined_id'], i))
      sys.stderr.write('%s\n' % rdict)
      return num_err_rows + 1

    source_id = cid_matches.group(1)
    table_id = cid_matches.group(2)

    #if source_id != rdict['old_source_id']:
    #  sys.stderr.write('Mismatch of old source ID in row (%i)\n' % i)
    #  sys.stderr.write('%s\n' % rdict)
    #  return num_err_rows + 1

    table = None

    try:
      table = Table.objects.get(old_id = table_id)
    except Table.DoesNotExist as e:
      sys.stderr.write('Source table does not exist in row (%i)\n' % i)
      sys.stderr.write('%s\n' % rdict)
      return num_err_rows + 1

    #nr = cid_matches.group(3)

    #if not nr and table.nr != nr:
    #  sys.stderr.write('Table NR mismatch in row (%i)\n' % i)
    #  sys.stderr.write('%s\n' % rdict)
    #  return num_err_rows + 1

    rdict['source'] = table
  else:
    source = None
    try:
      Source.objects.get(old_id = rdict['old_source_id'])
    except Source.DoesNotExist as e:
      sys.stderr.write('Source does not exist in row (%i)\n' % i)
      sys.stderr.write('%s\n' % rdict)
      return num_err_rows + 1
    rdict['source'] = source

  val_specified = False

  if rdict.has_key('individuals_population_value'): 
    if len(rdict['individuals_population_value']) > 0 and rdict['individuals_population_value'] != 0:
      val_specified = True
      rdict['individ_fam'] = 0
      rdict['population_value'] = rdict['individuals_population_value']

    del rdict['individuals_population_value']

  if rdict.has_key('families_population_value'): 
    if len(rdict['families_population_value']) > 0 and rdict['families_population_value'] != 0:    
      if val_specified:
        num_err_rows = add_row(rdict.copy(), num_err_rows)      
      else:
        val_specified = True
        rdict['individ_fam'] = 1
        rdict['population_value'] = rdict['families_population_value']

    del rdict['families_population_value']

  if rdict.has_key('male_population_value'): 
    if len(rdict['male_population_value']) > 0 and rdict['male_population_value'] != 0:
      if val_specified:
        num_err_rows = add_row(rdict.copy(), num_err_rows)
      else:
        val_specified = True
        rdict['individ_fam'] = 0
        rdict['population_value'] = rdict['male_population_value']
        rdict['population_gender'] = 'm'

    del rdict['male_population_value']

  if rdict.has_key('female_population_value'): 
    if len(rdict['female_population_value']) > 0 and rdict['female_population_value'] != 0:
      if val_specified:
       num_err_rows = add_row(rdict.copy(), num_err_rows)
      else:
        val_specified = True
        rdict['individ_fam'] = 0
        rdict['population_value'] = rdict['female_population_value']
        rdict['population_gender'] = 'f'

    del rdict['female_population_value']

  if not val_specified:
    #sys.stderr.write('Data entry with no data in row (%i)\n' % i)
    #sys.stderr.write('%s\n' % rdict)
    return num_err_rows + 1

  try:
    print i, rdict['place_origin'].decode(migtools.STRING_ENCODING), u", ", rdict['large1'].decode(migtools.STRING_ENCODING), u", ", rdict['large2'].decode(migtools.STRING_ENCODING), u", ", rdict['large3'].decode(migtools.STRING_ENCODING)
  except UnicodeEncodeError:
    # Windows decode error workaround
    print i, "<UnicodeEncodeError Encountered, ignoring for now>"

  try:
    rdict['location'] = migtools.get_or_add_location(unicode(rdict['place_origin'], migtools.STRING_ENCODING), mig_user, unicode(rdict['large1'], migtools.STRING_ENCODING), unicode(rdict['large2'], migtools.STRING_ENCODING), unicode(rdict['large3'], migtools.STRING_ENCODING))
  except Location.DatabaseError as e:
    sys.stderr.write('Database error on getting or adding location in row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    return num_err_rows + 1
  except migtools.LocationTooComplicated as e:
    sys.stderr.write('Location too complicated in row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    return num_err_rows + 1

  #import pdb; pdb.set_trace()

  del rdict['place_origin']
  del rdict['large1']
  del rdict['large2']
  del rdict['large3']
  del rdict['link']
  del rdict['place_english']

  # No longer storing these
  del rdict['old_combined_id']
  del rdict['old_source_id']
  
  for k in rdict.keys():
    if isinstance(rdict[k], basestring) and not rdict[k]:
      del rdict[k]

  for col_name, add_fun in { 'religion' : get_or_add_religion, 'race' : get_or_add_race, 'ethnicity' : get_or_add_ethnicity, 'ethnic_origin' : get_or_add_ethnic_origin, 'population_condition' : get_or_add_pop_cond }.iteritems():
    if rdict.has_key(col_name):
      try:
        rdict[col_name] = add_fun(unicode(rdict[col_name], migtools.STRING_ENCODING))
      except DatabaseError as e:
        sys.stderr.write("Error on get_or_add_%s in row (%i): %s\n" % (col_name, i, e))
        sys.stderr.write("%s\n" % rdict)
        return num_err_rows + 1

  if rdict.has_key('remarks'):
    rdict['remarks'] = rdict['remarks'].decode(migtools.STRING_ENCODING)

  if rdict.has_key('alternate_location_name'):
    rdict['alternate_location_name'] = rdict['alternate_location_name'].decode(migtools.STRING_ENCODING)

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
    return num_err_rows + 1

  for age_col in ('age_start', 'age_end'):
    if rdict.has_key(age_col):
      if rdict[age_col] == 'Unknown':
        del rdict[age_col]
      elif rdict[age_col] in ('Under 1', 'Total', 'Total all ages', 'All ages'):
        del rdict['age_start']
        if rdict.has_key('age_end'): del rdict['age_end'] 
        break
      elif rdict[age_col] in ('Not specified','Unspecified', 'Period not indicated'):
        del rdict[age_col]
      else:
        over_match = re.match(r'Over\s(\d+)', rdict[age_col])
        if over_match:
          if rdict.has_key('age_end'): del rdict['age_end'] 
          rdict['age_start'] = over_match.group(1) 
          break

        under_match = re.match(r'Under\s(\d+)', rdict[age_col])
        if under_match:
          if rdict.has_key('age_start'): del rdict['age_start']
          rdict['age_end'] = under_match.group(1)
          break

        total_range_match = re.match(r'Total,\s(\d+)-(\d+)', rdict[age_col])
        if total_range_match:
          rdict['age_start'] = total_range_match.group(1)
          rdict['age_end'] = total_range_match.group(2)
          break

  rdict['active'] = True
  rdict['submitted_by'] = mig_user 
          
  try:
    entry = MainDataEntry(**rdict)
    entry.save()
  except (ValueError, DatabaseError, ValidationError) as e:
    sys.stderr.write('Failed to save data row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    num_err_rows += 1

  return num_err_rows

# Script begins ###############################################################################                                                       

infile = sys.argv[1]
reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

num_err_rows = 0

for i, row in enumerate(reader):
  rdict = dict(zip(('old_source_id', 'old_combined_id', 'primary_source', 'page_num', 'begin_date', 'end_date', 'place_origin', 'place_english', 'alternate_location_name', 'large1', 'large2', 'large3', 'religion', 'race', 'ethnicity', 'ethnic_origin', 'age_start', 'age_end', 'remarks', 'link', 'individuals_population_value', 'families_population_value', 'male_population_value', 'female_population_value', 'value_unit', 'is_total', 'population_condition', 'polity', 'iso', 'wb'), row))

  #if rdict['place_english'] or rdict['alternate_location_name'] : 
  #  print i, rdict['place_origin'], ", ", rdict['alternate_location_name'], ", ", rdict['place_english']
  #continue 

  #if i < 91580: continue

  num_err_rows = add_row(rdict, num_err_rows)

print 'Migration complete. %i row errors encountered and ignored' % num_err_rows
