#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools
import string

import migtools

from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location
from colonialismdb.sources.models import Source
from colonialismdb.economics.models import BilateralTradeDataEntry

mig_user = User.objects.get(username = 'datamiguser')
src = Source.objects.get(pk = 3381)

if __name__ == "__main__":
  infile = sys.argv[1]
  loc_name = sys.argv[2]

  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  locs = Location.objects.filter(name__iexact = loc_name).filter(politically_in = None)[:1]
  loc = None

  if len(locs) == 0:
    loc = Location(name = loc_name, submitted_by = mig_user)
    loc.save()
  else:
    loc = locs[0]

  exp_imp = None
  partners = list()

  for i, row in enumerate(reader):
    if i == 0:
      exp_imp = row[1:]
    elif i == 1:
      prev_partner = None
      for partner_name in row[1:]:
        if prev_partner and (prev_partner.name.lower() == partner_name.lower()):
          partners.append(prev_partner)
        else:
          locs = Location.objects.filter(name__iexact = partner_name).filter(politically_in = None)[:1]

          if len(locs) == 0:
            new_loc = Location(name = partner_name, submitted_by = mig_user)
            new_loc.save()
            partners.append(new_loc)
            prev_partner = new_loc
          else:
            partners.append(locs[0])
            prev_partner = locs[0]
    else:
      year = int(row[0])
      begin_year = datetime.date(year, 1, 1)
      end_year = datetime.date(year, 12, 31)

      def clean_trade(t):
        try: 
          f = float(string.replace(t, ',', '')) if t else None
          return unicode(f) if f and (f != 0) else None 
        except ValueError: 
          return None

      trade = map(clean_trade, row[1:])

      i = 0
      
      while i < len(trade):
        if (exp_imp[i] == "imports") and ((i + 1) < len(trade)) and partners[i] == partners[i + 1]:
          new_data = BilateralTradeDataEntry(location = loc, 
                                             trade_partner = partners[i], 
                                             imports = trade[i],
                                             exports = trade[i + 1],
                                             begin_date = begin_year,
                                             end_date = end_year,
                                             source = src,
                                             submitted_by = mig_user)
          new_data.save()
          i += 1
        elif trade[i]:
          kwargs = { 'location' : loc, 
                     'trade_partner' : partners[i], 
                     exp_imp[i] : trade[i], 
                     'begin_date' : begin_year,
                     'end_date' : end_year,
                     'source' : src,
                     'submitted_by' : mig_user } 
          new_data = BilateralTradeDataEntry(**kwargs)
          new_data.save()

        i += 1


