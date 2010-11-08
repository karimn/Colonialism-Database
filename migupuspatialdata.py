#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

from colonialismdb.government.models import MainDataEntry
from colonialismdb.common.models import Location, SpatialAreaUnit
from colonialismdb.sources.models import Source, Table

from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Script begins ###############################################################################                                                       

if __name__ == "__main__":
  infile = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter=',', quotechar = '"')

  num_err_rows = 0
  num_mig = 0
  num_locs = 0

  src = None
  
  if len(sys.argv) > 2:
    src = Table.objects.get(pk = int(sys.argv[2]))
  else:
    src = Table.objects.get(pk = 3391)

  for i, row in enumerate(reader):
    if i < 1:
      continue

    rdict = dict(zip(("location", "begin_date", "end_date", "spatial_area", "spatial_area_unit", "table_num", "source", "primary_source"), row))

    locs = Location.objects.filter(name__iexact = rdict["location"]).filter(politically_in = None)[:1]
    if len(locs) == 0:
      rdict["location"] = Location(name = rdict["location"], submitted_by = migtools.mig_user)
      rdict["location"].save()
      num_locs += 1
    else:
      rdict["location"] = locs[0]

    rdict["begin_date"] = datetime.date(int(rdict["begin_date"]), 1, 1)
    rdict["end_date"] = datetime.date(int(rdict["end_date"]), 12, 31)

    try:
      rdict["spatial_area_unit"] = SpatialAreaUnit.objects.get(name__iexact = rdict["spatial_area_unit"])
    except SpatialAreaUnit.DoesNotExist:
      sys.stderr.write("Unexpected spatial area unit(row %i): %s\n" % (i, rdict["spatial_area_unit"])) 
      num_err_rows += 1 
      continue

    if rdict["table_num"] == "1.1":
      del rdict["table_num"]
      rdict["source"] = src
    else:
      sys.stderr.write("Unexpected table number (row %i): %s\n" % (i, rdict["table_num"])) 
      num_err_rows += 1 
      continue

    rdict["active"] = True
    rdict["submitted_by"] = migtools.mig_user
    
    try:
      entry = MainDataEntry(**rdict)
      entry.save()
      num_mig += 1
      sys.stdout.write("[%i]\n" % i)
    except (ValueError, DatabaseError, ValidationError) as e:
      sys.stderr.write('Failed to save data row (%i): %s\n' % (i, e))
      num_err_rows += 1

  print 'Migration complete. %i rows migrated, %i locations created, and %i row errors encountered and ignored' % (num_mig, num_locs, num_err_rows)
