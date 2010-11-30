#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

from colonialismdb.economics.models import BilateralTradeDataEntry 
from colonialismdb.sources.models import Source, Table
from colonialismdb.common.models import Location

from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q

def convert_to_nominal(trade, ppi, base = 100.2):
  return trade * (ppi/base)

if __name__ == "__main__":
  codebook = sys.argv[1]
  codebook_reader = csv.reader(migtools.UTF8Recoder(open(codebook, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')
  codebook_dict = {}

  for i, row in enumerate(codebook_reader):
    codebook_dict[row[0]] = row[1]

  src = Source.objects.get(pk = 3381)
  
  infile = sys.argv[2]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  num_err_rows = 0
  num_excluded = 0
  locs_excluded = 0
  num_mig = 0
  new_locs_added = set()

  for i, row in enumerate(reader):
    if i < 1:
      continue

    rdict = dict(zip(('location', 'trade_partner', 'year', 'imports_exchange_rate', 'exports_exchange_rate', 'gfd_exchange_rate', 'exchange_rate_scalar', 'imports', 'exports', 'ppi'), row[3:6] + row[8:11] +row[12:13] + row[14:]))

    rdict = dict(filter(lambda x: x[1] and (x[1] != "#DIV/0!") and (x[1] != "#VALUE!"), rdict.items())) 

    if (not rdict.has_key("imports")) and (not rdict.has_key("exports")):
      num_excluded += 1
      sys.stdout.write("[%i] No data -- excluded\n" % i)
      continue

    if rdict.has_key("imports"):
      rdict["imports"] = str(convert_to_nominal(float(rdict["imports"]), float(rdict["ppi"])))
    if rdict.has_key("exports"):
      rdict["exports"] = str(convert_to_nominal(float(rdict["exports"]), float(rdict["ppi"])))

    del rdict["ppi"]

    for loc_name in ('location', 'trade_partner'):
      if codebook_dict.has_key(rdict[loc_name]):
        locs = Location.objects.filter(Q(name__iexact = codebook_dict[rdict[loc_name]]), Q(politically_in = None))
        if len(locs) > 0:
          rdict[loc_name] = locs[0]
        else:
          rdict[loc_name] = Location(name = codebook_dict[rdict[loc_name]], submitted_by = migtools.mig_user, active = True) 
          rdict[loc_name].save()
          new_locs_added.add(rdict[loc_name].name)
      else:
        locs_excluded += 1
        sys.stdout.write("[%i] Location '%s' excluded\n" % (i, rdict[loc_name]))
        continue

    rdict["begin_date"] = datetime.date(int(float(rdict["year"])), 1, 1)
    rdict["end_date"] = datetime.date(int(float(rdict["year"])), 12, 31)
    del rdict["year"]

    rdict["active"] = True
    rdict["submitted_by"] = migtools.mig_user

    rdict["source"] = src

    try:
      entry = BilateralTradeDataEntry(**rdict)
      entry.save()
      num_mig += 1
      sys.stdout.write("[%i] %s\n" % (i, entry))
    except (ValueError, DatabaseError, ValidationError) as e:
      sys.stderr.write('[%i] Failed to save data row: %s\n' % (i, e))
      num_err_rows += 1

  print 'Migration complete. %i rows migrated, %i rows excluded, %i locations excluded, and %i row errors encountered and ignored' % (num_mig, num_excluded, locs_excluded, num_err_rows)
  if len(new_locs_added) > 0:
    print("Locations added: %s" % (", ".join(new_locs_added)))
