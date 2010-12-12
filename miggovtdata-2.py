#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

from colonialismdb.government.models import SpatialAreaUnit, Currency, RevenueType, ExpenditureType, MoneySupplyType, MilitaryType, OfficialsType, MainDataEntry, PublicDebtType
from colonialismdb.common.models import Location, Religion, Ethnicity, EthnicOrigin, Race
from colonialismdb.sources.models import Source, Table
from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from reversion import revision
 
get_or_add_area_unit = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = SpatialAreaUnit)
get_or_add_currency = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = Currency)
get_or_add_revenue_type = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = RevenueType)
get_or_add_expenditure_type = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = ExpenditureType)
get_or_add_money_supply_type = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = MoneySupplyType)
get_or_add_military_type = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = MilitaryType)
get_or_add_officials_type = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = OfficialsType)
get_or_add_public_debt_type = functools.partial(migtools.get_or_add_cat_item, mig_user = migtools.mig_user, cat = PublicDebtType)

strip_dollar = functools.partial(migtools.strip_rdict, chars = "$")
replace_decimal_comma = functools.partial(migtools.replace_decimal_comma, exclude_columns = ('currency_exchange_rate', 'remarks'))

# Script begins ###############################################################################                                                       

if __name__ == "__main__":
  infile = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  num_err_rows = 0

  for i, row in enumerate(reader):
    rdict = dict(zip(('source', 'page_num', 'primary_source_text', 'begin_date', 'end_date', 'original_location_name', 'place_english', 'alternate_location_name', 'large1', 'large2', 'large3', 'spatial_area', 'spatial_area_unit', 'currency', 'currency_exchange_rate', 'revenue', 'revenue_type', 'expenditure', 'expenditure_type', 'public_debt', 'public_debt_type', 'military', 'military_type', 'officials', 'other', 'remarks', 'link', 'value_unit', 'is_total', ), row[1:2] + row[3:32]))

    if rdict.has_key('other'):
      del rdict['other']

    #if rdict['place_english'] or rdict['alternate_location_name'] : 
    #  print i, rdict['place_origin'], ", ", rdict['alternate_location_name'], ", ", rdict['place_english']
    #continue 

    #if i < 91580: continue

    #num_err_rows = add_row(rdict, num_err_rows)

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
                                                        rdict['large3'].decode(migtools.STRING_ENCODING)))
    except DatabaseError as e:
      sys.stderr.write('[%i] Database error on getting or adding location: %s: %s\n' % (i, e, rdict))
      num_err_rows += 1
      continue
    except migtools.LocationTooComplicated as e:
      sys.stderr.write('[%i] Location too complicated: %s: %s\n' % (i, e, rdict))
      num_err_rows += 1
      continue

    del rdict['large1']
    del rdict['large2']
    del rdict['large3']
    del rdict['link']
    del rdict['place_english']

    rdict = dict(map(migtools.strip_rdict, rdict.items())) # Remove blank strings
    rdict = dict(map(strip_dollar, rdict.items())) # Remove dollar signs
    rdict = dict(map(replace_decimal_comma, rdict.items())) # Remove decimal commas
    rdict = dict(filter(lambda x: x[1], rdict.items())) # removing null values

    if rdict.has_key('value_unit') and rdict['value_unit'] == "undefined":
      del rdict['value_unit']

    for col_name, add_fun in { 'spatial_area_unit' : get_or_add_area_unit, 
                               'currency' : get_or_add_currency, 
                               'revenue_type' : get_or_add_revenue_type, 
                               'expenditure_type' : get_or_add_expenditure_type, 
                               'money_supply_type': get_or_add_money_supply_type, 
                               'military_type' : get_or_add_military_type,
                               'officials_type' : get_or_add_officials_type,
                               'public_debt_type' : get_or_add_public_debt_type, }.iteritems():
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
        date_parts = [int(j) for j in rdict['begin_date'].split(' ')[0].split('/')]
        if len(date_parts) > 1:
          mon, day, year = date_parts
          rdict['begin_date'] = datetime.date(year, mon, day)
        else:
          rdict['begin_date'] = datetime.date(date_parts[0], 1, 1)

      if rdict.has_key('end_date'):
        date_parts = [int(j) for j in rdict['end_date'].split(' ')[0].split('/')]
        if len(date_parts) > 1:
          mon, day, year = date_parts
          rdict['end_date'] = datetime.date(year, mon, day)
        else:
          rdict['end_date'] = datetime.date(date_parts[0], 12, 31)
    except ValueError as e:
      sys.stderr.write('[%i] Encountered error in date format: %s: %s\n' % (i, e, rdict))
      num_err_rows += 1
      continue

    for dollar_field in ('revenue', 'expenditure'):
      if rdict.has_key(dollar_field):
        rev_match = re.match(r'(\d+\.\d\d)', rdict[dollar_field])

        if rev_match:
          rdict[dollar_field] = rev_match.group(1)
        else:
          rev_match = re.match(r'\(\$?(\d+\.\d\d)\)', rdict[dollar_field])
          if rev_match:
            rdict[dollar_field] = '-' + rev_match.group(1)
          else:
            sys.stderr.write('[%i] Unexpected %s format: %s\n' % (i, dollar_field, rdict))
            num_err_rows += 1
            continue

    if rdict.has_key('spatial_area'):
      rdict['spatial_area'] = rdict['spatial_area'].replace(',', '.').replace("approx.", "")

    rdict['active'] = True
    rdict['submitted_by'] = migtools.mig_user 
            
    try:
      entry = MainDataEntry(**rdict)
      entry.save()
    except (ValueError, DatabaseError, ValidationError) as e:
      sys.stderr.write('[%i] Failed to save data: %s: %s\n' % (i, e, rdict))
      num_err_rows += 1

  print 'Migration complete. %i row errors encountered and ignored' % num_err_rows
