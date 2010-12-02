#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools
import string

import migtools

from colonialismdb.population.models import MainDataEntry 
from colonialismdb.sources.models import Source, Table
from colonialismdb.common.models import Location

from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q

africa = Location.objects.get(Q(name = "Africa"), Q(geographically_in = None), Q(politically_in = None))

africa_regions_names = ("Subsaharan Africa", "West Africa", "Central Africa", "Northeast Africa", "East Africa", "Southern Africa", "North Africa")

begin_date_50 = datetime.date(1950, 1, 1)
end_date_50 = datetime.date(1950, 12, 31)
begin_date_60 = datetime.date(1960, 1, 1)
end_date_60 = datetime.date(1960, 12, 31)
    
if __name__ == "__main__":
  src = Source.objects.get(pk = 3400)
  
  infile = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  new_locs_added = set()

  africa_regions = dict()
  for region_name in africa_regions_names:
    region_matches = Location.objects.filter(Q(name__iexact = region_name), Q(geographically_in = africa), Q(politically_in = None))
    if len(region_matches) > 0:
      africa_regions[region_name] = region_matches[0]
    else:
      new_region = Location(name = region_name, geographically_in = africa, submitted_by = migtools.mig_user, active = True)
      new_region.save()
      new_locs_added.add(unicode(new_region))
      africa_regions[region_name] = new_region

  num_err_rows = 0
  num_mig = 0

  last_region = None
  last_country = None

  for i, row in enumerate(reader):
    if i < 1:
      continue

    rdict = dict(zip(('location', 'pop_50', 'pop_60'), row))

    in_country = rdict['location'][0] == ' '
    rdict['location'] = string.capwords(rdict['location'])

    if rdict['location'] == "Africa":
      rdict['location'] = africa
    elif rdict['location'] in africa_regions.keys():
      rdict['location'] = africa_regions[rdict['location']]
      last_region = rdict['location']
      last_country = None
    elif in_country: 
      rdict['location'] = rdict['location'].lstrip()
      if last_country:
        loc_matches = Location.objects.filter(Q(name__iexact = rdict['location']), Q(geographically_in = last_country), Q(politically_in = None))
        if len(loc_matches) > 0:
          rdict['location'] = loc_matches[0]
        else:
          new_loc = Location(name = rdict['location'], geographically_in = last_country, submitted_by = migtools.mig_user, active = True)
          new_loc.save()
          new_locs_added.add(unicode(new_loc))
          rdict['location'] = new_loc
      else:
        num_err_rows += 1
        sys.stderr.write("[%i] Country not found for %s" % (i, rdict['location']))
        continue
    else:
      if last_region:
        country_matches = Location.objects.filter(Q(name = rdict['location']), Q(geographically_in = last_region), Q(politically_in = None))
        if len(country_matches) > 0:
          last_country = rdict['location'] = country_matches[0]
        else:
          new_country = Location(name = rdict['location'], geographically_in = last_region, submitted_by = migtools.mig_user, active = True)
          new_country.save()
          new_locs_added.add(unicode(new_country))
          last_country = rdict['location'] = new_country 
      else:
        num_err_rows += 1
        sys.stderr.write("[%i] Region not found for %s" % (i, rdict['location']))
        continue

    rdict["active"] = True
    rdict["submitted_by"] = migtools.mig_user

    rdict["source"] = src

    pop_50 = rdict['pop_50'].replace(',', '')
    pop_60 = rdict['pop_60'].replace(',', '')

    del rdict['pop_50']
    del rdict['pop_60']

    rdict_50 = rdict.copy()
    rdict_60 = rdict.copy()

    rdict_50['begin_date'] = begin_date_50
    rdict_50['end_date'] = end_date_50
    rdict_50['population_value'] = pop_50
    rdict_60['begin_date'] = begin_date_60
    rdict_60['end_date'] = end_date_60
    rdict_60['population_value'] = pop_60

    try:
      entry_50 = MainDataEntry(**rdict_50)
      entry_50.save()
      num_mig += 1
      entry_60 = MainDataEntry(**rdict_60)
      entry_60.save()
      num_mig += 1
      sys.stdout.write("[%i] %s\n" % (i, rdict['location']))
    except (ValueError, DatabaseError, ValidationError) as e:
      sys.stderr.write('[%i] Failed to save data row: %s\n' % (i, e))
      num_err_rows += 1

  infile = sys.argv[2]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  last_region = None
  last_country = None

  for i, row in enumerate(reader):
    if i < 1:
      years = row[1:]
      continue

    location = row[0]
    pop_values = dict(zip(years, row[1:]))

    in_country = location[0] == ' '
    location = string.capwords(location)

    if location == "Africa":
      location = africa
    elif location in africa_regions.keys():
      location = africa_regions[location]
      last_region = location
      last_country = None
    elif in_country: 
      if last_country:
        loc_matches = Location.objects.filter(Q(name__iexact = location), Q(geographically_in = last_country), Q(politically_in = None))
        if len(loc_matches) > 0:
          location = loc_matches[0]
        else:
          new_loc = Location(name = location, geographically_in = last_country, submitted_by = migtools.mig_user, active = True)
          new_loc.save()
          new_locs_added.add(unicode(new_loc))
          location = new_loc
      else:
        num_err_rows += 1
        sys.stderr.write("[%i] Country not found for %s" % (i, location))
        continue
    else:
      if last_region:
        country_matches = Location.objects.filter(Q(name = location), Q(geographically_in = last_region), Q(politically_in = None))
        if len(country_matches) > 0:
          last_country = location = country_matches[0]
        else:
          new_country = Location(name = location, geographically_in = last_region, submitted_by = migtools.mig_user, active = True)
          new_country.save()
          new_locs_added.add(unicode(new_country))
          last_country = location = new_country 
      else:
        num_err_rows += 1
        sys.stderr.write("[%i] Region not found for %s" % (i, location))
        continue

    for year, pop_value in pop_values.iteritems():
      begin_date = datetime.date(int(year), 1, 1)
      end_date = datetime.date(int(year), 12, 31)
      pop_value = pop_value.replace(',', '')
      if not pop_value:
        continue

      try:
        entry = MainDataEntry(location = location, 
                              source = src, 
                              submitted_by = migtools.mig_user, 
                              active = True, 
                              population_value = pop_value,
                              begin_date = begin_date,
                              end_date = end_date)
        entry.save()
        num_mig += 1
      except (ValueError, DatabaseError, ValidationError) as e:
        sys.stderr.write('[%i] Failed to save data row: %s\n' % (i, e))
        num_err_rows += 1
      else:
        sys.stdout.write("[%i] %s (%s)\n" % (i, location, year))

  print 'Migration complete. %i rows migrated, and %i row errors encountered and ignored' % (num_mig, num_err_rows)
  if len(new_locs_added) > 0:
    print("Locations added: %s" % (", ".join(new_locs_added)))
