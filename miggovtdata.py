#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

from colonialismdb.government.models import SpatialAreaUnit, Currency, RevenueType, ExpenditureType, MoneySupplyType, MilitaryType, OfficialsType, MainDataEntry
from colonialismdb.common.models import Location, Religion, Ethnicity, EthnicOrigin, Race
from colonialismdb.sources.models import Source, Table
from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from reversion import revision

mig_user = User.objects.get(username = 'karim')
 
get_or_add_area_unit = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = SpatialAreaUnit)
get_or_add_currency = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = Currency)
get_or_add_revenue_type = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = RevenueType)
get_or_add_expenditure_type = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = ExpenditureType)
get_or_add_money_supply_type = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = MoneySupplyType)
get_or_add_military_type = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = MilitaryType)
get_or_add_officials_type = functools.partial(migtools.get_or_add_cat_item, mig_user = mig_user, cat = OfficialsType)

# Script begins ###############################################################################                                                       

if __name__ == "__main__":
  infile = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  num_err_rows = 0

  for i, row in enumerate(reader):
    rdict = dict(zip(('old_source_id', 'old_combined_id', 'page_num', 'begin_date', 'end_date', 'place_origin', 'place_english', 'alternate_location_name', 'large1', 'large2', 'large3', 'spatial_area', 'spatial_area_unit', 'currency', 'currency_exchange_rate', 'revenue', 'revenue_type', 'expenditure', 'expenditure_type', 'public_debt', 'money_supply', 'money_supply_type', 'military', 'military_type', 'officials', 'officials_type', 'remarks', 'primary_source', 'link', 'value_unit', 'is_total', 'polity', 'iso', 'wb' ), row[1:]))

    #if rdict['place_english'] or rdict['alternate_location_name'] : 
    #  print i, rdict['place_origin'], ", ", rdict['alternate_location_name'], ", ", rdict['place_english']
    #continue 

    #if i < 91580: continue

    #num_err_rows = add_row(rdict, num_err_rows)
    
    if rdict['old_combined_id']:
      cid_matches = re.match(r'([^-]+)-([^\.]+)(?:\.(.+))', rdict['old_combined_id'])

      if not cid_matches:
        sys.stderr.write('Failed to match combined id %s in row (%i)\n' % (rdict['old_combined_id'], i))
        sys.stderr.write('%s\n' % rdict)
        num_err_rows += 1
        continue

      source_id = cid_matches.group(1)
      table_id = cid_matches.group(2)

      if source_id != rdict['old_source_id']:
        sys.stderr.write('Mismatch of old source ID in row (%i)\n' % i)
        sys.stderr.write('%s\n' % rdict)
        num_err_rows += 1
        continue

      table = None

      try:
        table = Table.objects.get(old_id = table_id)
      except Table.DoesNotExist as e:
        sys.stderr.write('Source table does not exist in row (%i)\n' % i)
        sys.stderr.write('%s\n' % rdict)
        num_err_rows += 1
        continue

      nr = cid_matches.group(3)

      if not nr and table.nr != nr:
        sys.stderr.write('Table NR mismatch in row (%i)\n' % i)
        sys.stderr.write('%s\n' % rdict)
        num_err_rows += 1
        continue

      rdict['source'] = table
    else:
      source = None

      try:
        Source.objects.get(old_id = rdict['old_source_id'])
      except Source.DoesNotExist as e:
        sys.stderr.write('Source does not exist in row (%i)\n' % i)
        sys.stderr.write('%s\n' % rdict)
        num_err_rows += 1
        continue

      rdict['source'] = source

    # No longer storing these
    del rdict['old_combined_id']
    del rdict['old_source_id']

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
      num_err_rows += 1
      continue
    except migtools.LocationTooComplicated as e:
      sys.stderr.write('Location too complicated in row (%i): %s\n' % (i, e))
      sys.stderr.write('%s\n' % rdict)
      num_err_rows += 1
      continue

    del rdict['place_origin']
    del rdict['large1']
    del rdict['large2']
    del rdict['large3']
    del rdict['link']
    del rdict['place_english']

    for k in rdict.keys():
      if isinstance(rdict[k], basestring) and not rdict[k]:
        del rdict[k]

    for col_name, add_fun in { 'spatial_area_unit' : get_or_add_area_unit, 
                               'currency' : get_or_add_currency, 
                               'revenue_type' : get_or_add_revenue_type, 
                               'expenditure_type' : get_or_add_expenditure_type, 
                               'money_supply_type': get_or_add_money_supply_type, 
                               'military_type' : get_or_add_military_type,
                               'officials_type' : get_or_add_officials_type, }.iteritems():
      if rdict.has_key(col_name):
        try:
          rdict[col_name] = add_fun(unicode(rdict[col_name], migtools.STRING_ENCODING))
        except DatabaseError as e:
          sys.stderr.write("Error on get_or_add_%s in row (%i): %s\n" % (col_name, i, e))
          sys.stderr.write("%s\n" % rdict)
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
        mon, day, year = [int(j) for j in rdict['begin_date'].split(' ')[0].split('/')]
        rdict['begin_date'] = datetime.date(year, mon, day)

      if rdict.has_key('end_date'):
        mon, day, year = [int(j) for j in rdict['end_date'].split(' ')[0].split('/')]
        rdict['end_date'] = datetime.date(year, mon, day)
    except ValueError as e:
      sys.stderr.write('Encountered error in date format at row (%i): %s\n' % (i, e))
      sys.stderr.write('%s\n' % rdict)
      num_err_rows += 1
      continue

    if rdict.has_key('revenue'):
      rev_match = re.match(r'\$(\d+\.\d\d)', rdict['revenue'])

      if rev_match:
        rdict['revenue'] = rev_match.group(1)
      else:
        sys.stderr.write('Unexpected revenue format in row (%i)\n' % (i, ))
        sys.stderr.write('%s\n' % rdict)
        num_err_rows += 1
        continue

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
