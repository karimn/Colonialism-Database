#!/usr/bin/python

import csv
import datetime
import sys
import re
import os
import functools

import migtools

from colonialismdb.sources.models import SourceSubject, DigitizationPriority, Source, Table
from colonialismdb.common.models import Language

from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

get_or_add_language = functools.partial(migtools.get_or_add_cat_item, cat = Language)
get_or_add_subject = functools.partial(migtools.get_or_add_cat_item, cat = SourceSubject)
get_or_add_priority = functools.partial(migtools.get_or_add_cat_item, cat = DigitizationPriority)

# Script begins ###############################################################################                                                       

if __name__ == "__main__":
  infile = sys.argv[1]
  reader = csv.reader(open(infile, "r"), delimiter='\t', quotechar = '"')

  num_err_rows = 0

  saved_row = None

  i = 0

  for j, row in enumerate(reader):
    if saved_row:
      if len(row) > 0:
        saved_row[len(saved_row) - 1] = saved_row[len(saved_row) - 1] + row[0]
        
        if len(row) > 1:
          saved_row[len(saved_row):] = row[1:]

      row = saved_row
      saved_row = None

    rdict = dict(zip(('old_id', 'old_source_id', 'nr', 'original_name', 'original_language', 'name', 'subjects', 'included_countries', 'begin_page', 'end_page', 'begin_year', 'end_year', 'prc', 'submitted_by', 'url', 'source_file', 'remarks', 'transfer', 'digitization_priority_gra', 'digitization_priority_pi', 'record_date'), row))

    if not rdict.has_key('record_date'):
      saved_row = row
      continue

    i += 1

    #if i < 2645: continue
    #if i == 2645: import pdb; pdb.set_trace()

    del rdict['transfer']

    if re.match(r'^#?http:', rdict['source_file']):
      if not rdict.has_key('url'):
        rdict['url'] = rdict['source_file']
      else:
        sys.stderr.write('URL already specified in row (%i)\n' % i)
        sys.stderr.write('%s\n' % rdict)
        num_err_rows += 1
        continue 

      del rdict['source_file']

    source_file_path = None

    if os.environ.has_key('COLONIALISM_SERVER') and rdict.has_key('source_file') and rdict['source_file']: # and colonialism.settings.MEDIA_ROOT:
      source_file_path, num_err_rows = migtools.get_source_file_path(rdict, i, num_err_rows) 

      if not source_file_path:
        continue
      
    if rdict.has_key('source_file'):
      del rdict['source_file']

    try:
      rdict['source'] = Source.objects.get(old_id = rdict['old_source_id'])
    except Source.DoesNotExist as e:
      sys.stderr.write('Source %s not found from row (%i)\n' % (rdict['old_source_id'], i))
      sys.stderr.write('%s\n' % rdict)
      num_err_rows += 1
      continue

    rdict['name'] = unicode(rdict['name'], migtools.STRING_ENCODING)

    if rdict['original_name']:
      rdict['original_name'] = unicode(rdict['original_name'], migtools.STRING_ENCODING)

    rdict['remarks'] = unicode(rdict['remarks'], migtools.STRING_ENCODING)

    rdict['active'] = True

    if not rdict['submitted_by'] or len(rdict['submitted_by']) == 0:
      rdict['submitted_by'] = None
    else:
      try:
        rdict['submitted_by'] = User.objects.get(first_name__iexact = rdict['submitted_by'])
      except User.DoesNotExist as e:
        sys.stderr.write('Curator %s not found from row (%i)\n' % (rdict['submitted_by'], i))
        sys.stderr.write('%s\n' % rdict)
        num_err_rows += 1
        continue

    if rdict['original_language'] and len(rdict['original_language']) != 0:
      languages = [get_or_add_language(lang, rdict['submitted_by']) for lang in re.split(r'\s*,\s*', rdict['original_language'])]

    del rdict['original_language']

    subjects = None

    if rdict['subjects'] and len(rdict['subjects']) != 0:
      subjects = [get_or_add_subject(subject, rdict['submitted_by']) for subject in re.split('\s*,\s*', rdict['subjects'])]

    del rdict['subjects']

    if rdict['included_countries'] and len(rdict['included_countries']) != 0:
      try:
        countries = [migtools.get_or_add_location(unicode(country, migtools.STRING_ENCODING), rdict['submitted_by']) for country in re.split('\s*,\s*', rdict['included_countries'])]
      except migtools.LocationTooComplicated as e:
        sys.stderr.write('Location too complicated in row (%i): %s\n' % (i, e))
        sys.stderr.write('%s\n' % rdict)
        num_err_rows + 1
        continue

    del rdict['included_countries']

    if rdict['begin_year']:
      rdict['begin_year'] = re.match(r'\d+/\d+/(\d+)', rdict['begin_year']).group(1)
    else:
      del rdict['begin_year']

    if rdict['end_year']:
      rdict['end_year'] = re.match(r'\d+/\d+/(\d+)', rdict['end_year']).group(1)
    else:
      del rdict['end_year']

    if not rdict['url'] or len(rdict['url']) == 0:
      del rdict['url']
    else:
      url_match = re.search("#([^#]+)#", rdict['url'])

    rdict['digitization_priority_gra'] = get_or_add_priority(rdict['digitization_priority_gra'], rdict['submitted_by'])
    rdict['digitization_priority_pi'] = get_or_add_priority(rdict['digitization_priority_pi'], rdict['submitted_by'])

    if rdict['record_date']:
      record_date_matches = re.match(r'(\d+)/(\d+)/(\d+)', rdict['record_date'])

      if not record_date_matches:
        sys.stderr.write('Could not match record date in row (%i)\n' % (i,))
        sys.stderr.write('%s\n' % rdict)
        num_err_rows + 1
        continue
      else:
        rdict['record_date'] = datetime.date(int(record_date_matches.group(3)),
                                             int(record_date_matches.group(1)),
                                             int(record_date_matches.group(2)))
    else:
      del rdict['record_date']

    for k in rdict.keys():
      if not rdict[k] or (isinstance(rdict[k], basestring) and len(rdict[k]) == 0):
        del rdict[k]

    try:
      print "%i, %s" % (i, rdict['name'])
    except UnicodeEncodeError:
      # Windows decode error workaround
      print i, ", <UnicodeEncodeError Encountered, ignoring for now>"

    try:
      table = Table(**rdict)
      table.save()

      if countries:
        for country in countries:
          table.included_countries.add(country)

      if subjects:
        for subj in subjects:
          table.subjects.add(subj)

      if languages:
        for lang in languages:
          table.languages.add(lang)

      if source_file_path:
        if not migtools.add_source_files(source_file_path, table, rdict['submitted_by']):
          sys.stderr.write('Error on adding source file(s) (from) %s in row (%i)\n' % (source_file_path, i))
          sys.stderr.write('%s\n' % rdict)
          num_err_rows += 1
          table.delete()
          continue 
    except (ValueError, DatabaseError, ValidationError) as e:
      sys.stderr.write('Failed to save table row (%i): %s\n' % (i, e))
      sys.stderr.write('%s\n' % rdict)
      num_err_rows += 1

  print 'Migration complete. %i row errors encountered and ignored' % num_err_rows
