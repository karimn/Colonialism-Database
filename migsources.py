#!/usr/bin/python

import csv
import datetime
import sys
import os
import re
import functools

import migtools

from colonialismdb.sources.models import SourceType, SourceSubject, DigitizationPriority, Source
from colonialismdb.common.models import Language

from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

get_or_add_language = functools.partial(migtools.get_or_add_cat_item, cat = Language)
get_or_add_sourcetype = functools.partial(migtools.get_or_add_cat_item, cat = SourceType)
get_or_add_subject = functools.partial(migtools.get_or_add_cat_item, cat = SourceSubject)
get_or_add_priority = functools.partial(migtools.get_or_add_cat_item, cat = DigitizationPriority)

# Script begins ###############################################################################                                                       

infile = sys.argv[1]
reader = csv.reader(migtools.UTF8Recorder(open(infile, "r"), "utf-8"), delimiter='\t', quotechar = '"')

num_err_rows = 0

for i, row in enumerate(reader):
  rdict = dict(zip(('old_id', 'author', 'editor', 'original_title', 'title', 'year', 'publisher', 'city', 'series', 'volume', 'edition', 'isbn', 'total_pages', 'scanned_size', 'written_language1', 'written_language2', 'source_type', 'subjects', 'keywords', 'location', 'url', 'source_file', 'remarks', 'submitted_by', 'transfer', 'digitization_priority_gra', 'digitization_priority_pi', 'record_date'), row))

  #if i < 1: continue

  del rdict['transfer']

  rdict['active'] = True

  if rdict['year']:
    rdict['year'] = rdict['year'].split(' ')[0].split('/')[2]

  try:
    rdict['submitted_by'] = User.objects.get(first_name = rdict['submitted_by'])
  except User.DoesNotExist as e:
    sys.stderr.write('Curator %s not found from row (%i)\n' % (rdict['submitted_by'], i))
    sys.stderr.write('%s\n' % rdict)
    num_err_rows += 1
    continue 

  written_language1 = get_or_add_language(rdict['written_language1'], rdict['submitted_by'])
  written_language2 = get_or_add_language(rdict['written_language2'], rdict['submitted_by'])

  del rdict['written_language1']
  del rdict['written_language2']

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
    mon, day, year = [int(j) for j in rdict['record_date'].split(' ')[0].split('/')]
    rdict['record_date'] = datetime.date(year, mon, day)

  if not rdict['url'] or len(rdict['url']) == 0:
    del rdict['url']
  else:
    url_match = re.search("#([^#]+)#", rdict['url'])
    
    if url_match:
      rdict['url'] = url_match.group(1)
    else:
      sys.stderr.write('Failed to match url in row (%i)\n' % (i,))
      sys.stderr.write('%s\n' % rdict)
      num_err_rows += 1
      continue 

  print '%i, %s, %s, %s' % (i, rdict['author'], rdict['editor'], rdict['title'])

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

  for k in rdict.keys():
    if not rdict[k] or (isinstance(rdict[k], basestring) and len(rdict[k]) == 0):
      del rdict[k]


  for key in ('original_title', 'title', 'publisher', 'remarks'):
    if rdict.has_key(key):
      rdict[key] = unicode(rdict[key], migtools.STRING_ENCODING)

  try:
    source = Source(**rdict)
    source.save()

    if subjects:
      for subj in subjects:
        source.subjects.add(subj)

    if written_language1:
      source.languages.add(written_language1)

    if written_language2:
      source.languages.add(written_language2)

    if source_file_path:
      if not migtools.add_source_files(unicode(source_file_path, migtools.STRING_ENCODING), source, rdict['submitted_by']):
        sys.stderr.write('Error on adding source file(s) (from) %s in row (%i)\n' % (source_file_path, i))
        sys.stderr.write('%s\n' % rdict)
        num_err_rows += 1
        source.delete()
        continue 

  except (ValueError, DatabaseError, ValidationError) as e:
    sys.stderr.write('Failed to save source row (%i): %s\n' % (i, e))
    sys.stderr.write('%s\n' % rdict)
    num_err_rows += 1

print 'Migration complete. %i row errors encountered and ignored' % num_err_rows
