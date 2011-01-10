#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools
import argparse

import migtools

from colonialismdb.population.models import MainDataEntry, PopulationCondition
from colonialismdb.common.models import Location, Religion, Ethnicity, EthnicOrigin, Race
from colonialismdb.sources.models import Source, Table
from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from reversion import revision

get_or_add_religion = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = Religion)
get_or_add_race = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = Race)
get_or_add_ethnicity = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = Ethnicity)
get_or_add_ethnic_origin = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = EthnicOrigin)
get_or_add_pop_cond = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = PopulationCondition)

year_re = re.compile(r"\d{4}")

# Script begins ###############################################################################                                                       

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--allownewloc", action = 'store_true')
  parser.add_argument("infile")
  args = parser.parse_args()

  reader = csv.reader(migtools.UTF8Recoder(open(args.infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  num_err_rows = 0

  for i, row in enumerate(reader):
    rdict = dict(zip(('source', 'primary_source_text', 'page_num', 'begin_date', 'end_date', 'original_location_name', 'place_english', 'alternate_location_name', 'large1', 'large2', 'large3', 'religion', 'race', 'ethnicity', 'ethnic_origin', 'age_start', 'age_end', 'remarks', 'pop_value_individuals', 'pop_value_families', 'pop_value_males', 'pop_value_females', 'value_unit', 'is_total', 'population_condition'), row[0:1] + row[2:19] + row[20:]))

    if not rdict['source']:
      sys.stdout.write("[%i] No source -- skipping: %s\n" % (i, rdict))
      continue

    rdict['source'] = Source.objects.get(pk = rdict['source'])

    if not rdict['place_english'] and rdict['original_location_name']:
      rdict['place_english'] = rdict['original_location_name']

    try:
      sys.stdout.write("[%i] %s, %s, %s, %s\n" % (i,
                                                  rdict['place_english'].decode(migtools.STRING_ENCODING), 
                                                  rdict['large1'].decode(migtools.STRING_ENCODING), 
                                                  rdict['large2'].decode(migtools.STRING_ENCODING), 
                                                  rdict['large3'].decode(migtools.STRING_ENCODING)))
    except UnicodeEncodeError:
      # Windows decode error workaround
      sys.stdout.write("[%i] <UnicodeEncodeError Encountered, ignoring for now>\n" % i)

    try:
      rdict['location'] = migtools.get_or_add_location((rdict['place_english'].decode(migtools.STRING_ENCODING), 
                                                        rdict['large1'].decode(migtools.STRING_ENCODING),
                                                        rdict['large2'].decode(migtools.STRING_ENCODING),
                                                        rdict['large3'].decode(migtools.STRING_ENCODING),
                                                        args.allownewloc))
    except DatabaseError as e:
      sys.stderr.write('[%i] Database error on getting or adding location: %s: %s\n' % (i, e, rdict))
      num_err_rows += 1
      continue
    except migtools.LocationTooComplicated as e:
      sys.stderr.write('[%i] Location too complicated: %s: %s\n' % (i, e, rdict))
      num_err_rows += 1
      continue
    except Location.DoesNotExist:
      sys.stderr.write("[%i] No existing location found to match: %s\n" % (i, rdict))
      num_err_rows += 1
      continue

    del rdict['large1']
    del rdict['large2']
    del rdict['large3']
    del rdict['place_english']

    rdict = dict(map(migtools.strip_rdict, rdict.items())) # Remove blank strings
    #rdict = dict(map(replace_decimal_comma, rdict.items())) # Remove decimal commas
    rdict = dict(filter(lambda x: x[1], rdict.items())) # removing null values

    #if rdict.has_key('value_unit') and rdict['value_unit'] == "undefined":
    #  del rdict['value_unit']

    for col_name, add_fun in { 'religion' : get_or_add_religion,
                               'race' : get_or_add_race,
                               'ethnicity' : get_or_add_ethnicity,
                               'ethnic_origin' : get_or_add_ethnic_origin, 
                               'population_condition' : get_or_add_pop_cond, }.iteritems():
      if rdict.has_key(col_name):
        try:
          rdict[col_name] = add_fun(unicode(rdict[col_name], migtools.STRING_ENCODING))
        except DatabaseError as e:
          sys.stderr.write("[%i] Error on get_or_add_%s: %s: %s\n" % (i, col_name, e, rdict))
          num_err_rows += 1
          continue

    if rdict.has_key('remarks'):
      rdict['remarks'] = rdict['remarks'].decode(migtools.STRING_ENCODING)
      
    if rdict.has_key('primary_source'):
      rdict['primary_source'] = rdict['primary_source'].decode(migtools.STRING_ENCODING)

    if rdict.has_key('alternate_location_name'):
      rdict['alternate_location_name'] = rdict['alternate_location_name'].decode(migtools.STRING_ENCODING)

    try:
      if rdict.has_key('begin_date'):
        date_parts = rdict['begin_date'].split(' ')[0].split('/')
        if len(date_parts) == 3:
          mon, day, year = date_parts
          rdict['begin_date'] = datetime.date(int(year), int(mon), int(day))
        elif (len(date_parts) == 2) and (len(date_parts[0]) == 4) and (len(date_parts[1]) == 2):
          begin_year = date_parts[0]
          end_year = "19" + date_parts[1] 
          rdict['begin_date'] = datetime.date(int(begin_year), 1, 1)
          rdict['end_date'] = end_year 
        else:
          year_matches = year_re.match(date_parts[0])
          if not year_matches:
            sys.stderr.write("[%i] Invalid date format: %s\n" % (i, rdict))
            num_err_rows += 1
            continue
          rdict['begin_date'] = datetime.date(int(year_matches.group(0)), 1, 1)

      if rdict.has_key('end_date'):
        date_parts = rdict['end_date'].split(' ')[0].split('/')
        if len(date_parts) > 1:
          mon, day, year = date_parts
          rdict['end_date'] = datetime.date(int(year), int(mon), int(day))
        else:
          year_matches = year_re.match(date_parts[0])
          if not year_matches:
            sys.stderr.write("[%i] Invalid date format: %s\n" % (i, rdict))
            num_err_rows += 1
            continue
          rdict['end_date'] = datetime.date(int(year_matches.group(0)), 12, 31)
    except ValueError as e:
      sys.stderr.write('[%i] Encountered error in date format: %s: %s\n' % (i, e, rdict))
      num_err_rows += 1
      continue

    rdict['active'] = True
    rdict['submitted_by'] = migtools.mig_user 

    for pop_col in ('pop_value_individuals', 'pop_value_families', 'pop_value_males', 'pop_value_females'): 
      if rdict.has_key(pop_col):
        rdict_copy = rdict.copy()
        rdict_copy['population_value'] = rdict_copy[pop_col]

        for pop_col2 in ('pop_value_individuals', 'pop_value_families', 'pop_value_males', 'pop_value_females'): 
          if rdict_copy.has_key(pop_col2):
            del rdict_copy[pop_col2]

        if pop_col == 'pop_value_families':
          rdict_copy['individ_fam'] = 1
        elif pop_col == 'pop_value_males':
          rdict_copy['population_gender'] = 'M'
        elif pop_col == 'pop_value_females':
          rdict_copy['population_gender'] = 'F'

        try:
          entry = MainDataEntry(**rdict_copy)
          entry.save()
        except (ValueError, DatabaseError, ValidationError) as e:
          sys.stderr.write('[%i] Failed to save data: %s: %s\n' % (i, e, rdict_copy))
          num_err_rows += 1

  print 'Migration complete. %i row errors encountered and ignored' % num_err_rows
