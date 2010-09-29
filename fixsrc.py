#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

from colonialismdb.population.models import MainDataEntry, PopulationCondition
from colonialismdb.common.models import Location, Religion, Ethnicity, EthnicOrigin, Race
from colonialismdb.sources.models import Source, Table, BaseSourceObject
from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from reversion import revision

# Script begins ###############################################################################                                                       

if __name__ == "__main__":
  """
  null_src = []
  null_src_file = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(null_src_file, "r"), migtools.STRING_ENCODING), delimiter='|', quotechar = '"')

  for i, row in enumerate(reader):
    if i < 3:
      continue

    rdict = dict(zip(('begin_date', 'end_date', 'name', 'full_name', 'value'), row))

    begin_date = datetime.datetime.strptime(rdict['begin_date'].strip(), "%Y-%m-%d") if rdict['begin_date'].strip() else None
    end_date = datetime.datetime.strptime(rdict['end_date'].strip(), "%Y-%m-%d") if rdict['end_date'].strip() else None
    loc_name = rdict['name'].strip()
    value = rdict['value'].strip()

    null_src.append((begin_date, end_date, loc_name, value))

  mig = []
  """

  mig_file = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(mig_file, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  null_query = MainDataEntry.objects.filter(source = None)

  for i, row in enumerate(reader):
    rdict = dict(zip(('old_source_id', 'old_combined_id', 'primary_source', 'page_num', 'begin_date', 'end_date', 'place_origin', 'place_english', 'alternate_location_name', 'large1', 'large2', 'large3', 'religion', 'race', 'ethnicity', 'ethnic_origin', 'age_start', 'age_end', 'remarks', 'link', 'individuals_population_value', 'families_population_value', 'male_population_value', 'female_population_value', 'value_unit', 'is_total', 'population_condition', 'polity', 'iso', 'wb'), row))

    print("[%i]" % (i + 1))

    begin_date, end_date = None, None

    try:
      begin_date = datetime.datetime.strptime(rdict['begin_date'], "%m/%d/%Y") if rdict['begin_date'] else None
      end_date = datetime.datetime.strptime(rdict['end_date'], "%m/%d/%Y") if rdict['end_date'] else None
    except ValueError:
      continue

    for pop_val_name in ('individuals_population_value', 'families_population_value', 'male_population_value', 'female_population_value'):
      if len(rdict[pop_val_name]) > 0 and rdict[pop_val_name] != 0:
        #mig.append((begin_date, 
        #            end_date,
        #            rdict['place_origin'],
        #            rdict[pop_val_name],
        #            rdict['old_source_id']))

        q = null_query.filter(begin_date = begin_date).filter(end_date = end_date).filter(location__name = rdict['place_origin']).filter(population_value = rdict[pop_val_name])

        if q.count() > 0:
          if q.count() > 1:
            print("Too many matches")
          else:
            try:
              src = Source.objects.get(old_id = rdict['old_source_id'])
              q[0].source = src
              q[0].save()
              print("Source found: %s, %i" % (rdict['old_source_id'], q[0].id))
            except:
              print("Exception raised on finding and saving missing source")

