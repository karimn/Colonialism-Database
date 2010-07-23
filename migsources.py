#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

from colonialismdb.sources.models import Language, SourceType, SourceSubject, DigitizationPriority, Source

from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


#mig_user = User.objects.get(username = 'karim')

get_or_add_language = functools.partial(migtools.get_or_add_cat_item, cat = Language)
get_or_add_sourcetype = functools.partial(migtools.get_or_add_cat_item, cat = SourceType)
get_or_add_subject = functools.partial(migtools.get_or_add_cat_item, cat = SourceSubject)
get_or_add_priority = functools.partial(migtools.get_or_add_cat_item, cat = DigitizationPriority)

def add_row(rdict, num_err_rows):
  try:
    print i, rdict['place_origin'].decode(string_encoding), u", ", rdict['large1'].decode(string_encoding), u", ", rdict['large2'].decode(string_encoding), u", ", rdict['large3'].decode(string_encoding)
  except UnicodeEncodeError:
    # Windows decode error workaround
    print i, "<UnicodeEncodeError Encountered, ignoring for now>"

  try:
    rdict['location'] = get_or_add_location(unicode(rdict['place_origin'], string_encoding), unicode(rdict['large1'], string_encoding), unicode(rdict['large2'], string_encoding), unicode(rdict['large3'], string_encoding))
  except DatabaseError as e:
    sys.stderr.write('Database error on getting or adding location in row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    return num_err_rows + 1
  except LocationTooComplicated as e:
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
  
  for k in rdict.keys():
    if isinstance(rdict[k], basestring) and not rdict[k]:
      del rdict[k]

  for col_name, add_fun in { 'religion' : get_or_add_religion, 'race' : get_or_add_race, 'ethnicity' : get_or_add_ethnicity, 'ethnic_origin' : get_or_add_ethnic_origin, 'population_condition' : get_or_add_pop_cond }.iteritems():
    if rdict.has_key(col_name):
      try:
        rdict[col_name] = add_fun(rdict[col_name])
      except DatabaseError as e:
        sys.stderr.write("Error on get_or_add_%s in row (%i): %s\n" % (col_name, i, e))
        sys.stderr.write("%s\n" % rdict)
        return num_err_rows + 1

  if rdict.has_key('remarks'):
    rdict['remarks'] = rdict['remarks'].decode(string_encoding)

  if rdict.has_key('alternate_location_name'):
    rdict['alternate_location_name'] = rdict['alternate_location_name'].decode(string_encoding)

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
      elif rdict[age_col] in ('Under 1', 'Total', 'Total all ages'):
        del rdict['age_start']
        if rdict.has_key('age_end'): del rdict['age_end'] 
        break
      elif rdict[age_col] in ('Not specified',):
        del rdict[age_col]
      else:
        over_match = re.match(r'Over\s(\d+)', rdict[age_col])
        if over_match:
          if rdict.has_key('age_end'): del rdict['age_end'] 
          rdict['age_start'] = over_match.group(1) 
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
reader = csv.reader(open(infile, "r"), delimiter='\t', quotechar = '"')

string_encoding = 'ISO-8859-1'

num_err_rows = 0

for i, row in enumerate(reader):
  rdict = dict(zip(('old_id', 'author', 'editor', 'title', 'original_title', 'year', 'publisher', 'city', 'series', 'volume', 'edition', 'isbn', 'total_pages', 'scanned_size', 'written_language1', 'written_language2', 'source_type', 'subjects', 'keywords', 'location', 'url', 'source_file', 'remarks', 'submitted_by', 'transfer', 'digitization_priority_gra', 'digitization_priority_pi', 'record_date'), row))

  if i < 1: continue

  del rdict['transfer']

  rdict['active'] = True
  rdict['submitted_by'] = User.objects.get(first_name = rdict['submitted_by'])

  rdict['written_language1'] = get_or_add_language(rdict['written_language1'], rdict['submitted_by'])
  rdict['written_language2'] = get_or_add_language(rdict['written_language2'], rdict['submitted_by'])

  rdict['source_type'] = get_or_add_sourcetype(rdict['source_type'], rdict['submitted_by'])

  subjects = None

  if rdict['subjects'] and len(rdict['subjects']) != 0:
    subjects = [get_or_add_subject(subject, rdict['submitted_by']) for subject in re.split('\s*,\s*', rdict['subjects'])]

  del rdict['subjects']

  rdict['digitization_priority_gra'] = get_or_add_priority(rdict['digitization_priority_gra'], rdict['submitted_by'])
  rdict['digitization_priority_pi'] = get_or_add_priority(rdict['digitization_priority_pi'], rdict['submitted_by'])

  if not rdict['record_date'] or len(rdict['record_date']) == 0:
    del rdict['record_date']
  else:
    mon, day, year = [int(j) for j in rdict['record_date'].split('/')]
    rdict['record_date'] = datetime.date(year, mon, day)

  if not rdict['url'] or len(rdict['url']) == 0:
    del rdict['url']
  else:
    url_match = re.match("#([^#]+)#")
    
    if url_match:
      rdict['url'] = url_match.group(1)
    else:
      sys.stderr.write('Failed to match url in row (%i): %s\n' % (i,))
      sys.stderr.write('%s\n' % rdict)
      num_err_rows += 1
      continue 

  print '%i, %s, %s, %s' % (i, rdict['author'], rdict['editor'], rdict['title'])

  #TODO Adding files
  del rdict['source_file']

  for k in rdict.keys():
    if not rdict[k] or (isinstance(rdict[k], basestring) and len(rdict[k]) == 0):
      del rdict[k]

  try:
    source = Source(**rdict)
    source.save()
    source.subjects.add(subjects)
  except (ValueError, DatabaseError, ValidationError) as e:
    sys.stderr.write('Failed to save source row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    num_err_rows += 1

print 'Migration complete. %i row errors encountered and ignored' % num_err_rows
