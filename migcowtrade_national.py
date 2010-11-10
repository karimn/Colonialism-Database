#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

from colonialismdb.economics.models import AggregateTradeDataEntry
from colonialismdb.common.models import Location, Currency
from colonialismdb.sources.models import Source, Table

from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

primary_sources = { 1 : "Barbieri Version 1",
                    2 : "IMF import reports, in c.i.f. values (IMF, 2007)",
                    3 : "Missing import value replaced with the exporter's trade report, in f.o.b. values (IMF, 2007)",
                    4 : "Zero import trade value replaced with the exporter's trade report, in f.o.b. values (IMF, 2007)",
                    5 : "Missing import value replaced with importer's report, in c.i.f. values (IMF, 1992 tapes)",
                    6 : "Zero import trade value replaced with importer's report, in c.i.f. values (IMF, 1992 tapes)",
                    7 : "Missing import value replaced with exporter's report, in f.o.b. values (IMF, 1992 tapes)",
                    8 : "Zero import value replaced with exporter's report, in f.o.b. values (IMF, 1992 tapes)",
                    9 : "Missing values replaced with Barbieri trade values",
                    10 : "Zero values replaced with Barbieri trade values",
                    11 : "Belgium-Luxembourg Data 1948-2006 (see notes below)",
                    12 : "Taiwan Data from multiple sources (1952-1988)",
                    13 : "Data obtained from Aggregating China, Hong Kong and Macao", }

# Script begins ###############################################################################                                                       

if __name__ == "__main__":
  infile = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter=',', quotechar = '"')

  num_err_rows = 0
  num_mig = 0
  num_locs = 0

  src = None
  
  if len(sys.argv) > 2:
    src = Source.objects.get(pk = int(sys.argv[2]))
  else:
    src = Source.objects.get(pk = 3393)

  for i, row in enumerate(reader):
    if i < 1:
      continue

    rdict = dict(zip(("location", "year", "imports", "exports", "alt_imports", "alt_exports", "primary_source_1", "primary_source_2"), row[1:]))

    del rdict["alt_imports"]
    del rdict["alt_exports"]

    for loc_field in ("location", ):
      locs = Location.objects.filter(name__iexact = rdict[loc_field]).filter(politically_in = None)[:1]
      if len(locs) == 0:
        rdict[loc_field] = Location(name = rdict[loc_field], submitted_by = migtools.mig_user)
        rdict[loc_field].save()
        num_locs += 1
      else:
        rdict[loc_field] = locs[0]

    rdict["source"] = src

    rdict["begin_date"] = datetime.date(int(rdict["year"]), 1, 1)
    rdict["end_date"] = datetime.date(int(rdict["year"]), 12, 31)

    del rdict["year"]

    rdict["imports_value_unit"] = rdict["exports_value_unit"] = "millions"

    try:
      rdict["currency"] = Currency.objects.get(name = "US Dollars")
    except Currency.DoesNotExist:
      us_dollars = Currency(name = "US Dollars")
      us_dollars.save()
      rdict["currency"] = us_dollars

    rdict["primary_source"] = '' 

    if primary_sources.has_key(int(rdict["primary_source_1"])):
      rdict["primary_source"] = "imports: %s\n" % primary_sources[int(rdict["primary_source_1"])]
    if primary_sources.has_key(int(rdict["primary_source_2"])):
      rdict["primary_source"] += "exports: %s" % primary_sources[int(rdict["primary_source_2"])]

    if not rdict["primary_source"]:
      del rdict["primary_source"]

    del rdict["primary_source_1"]
    del rdict["primary_source_2"]

    rdict["active"] = True
    rdict["submitted_by"] = migtools.mig_user
    
    try:
      entry = AggregateTradeDataEntry(**rdict)
      entry.save()
      num_mig += 1
      sys.stdout.write("[%i] %s \n" % (i, entry.location))
    except (ValueError, DatabaseError, ValidationError) as e:
      sys.stderr.write('Failed to save data row (%i): %s\n' % (i, e))
      num_err_rows += 1

  print 'Migration complete. %i rows migrated, %i locations created, and %i row errors encountered and ignored' % (num_mig, num_locs, num_err_rows)
