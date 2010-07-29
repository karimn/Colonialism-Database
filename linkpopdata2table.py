#!/usr/bin/python

import re
import sys

from colonialismdb.population.models import MainDataEntry
from colonialismdb.sources.models import Table

num_err_rows = 0

for de in MainDataEntry.objects.all():
  cid_matches = re.match(r'([^-]+)-([^\.]+)\.(.+)', de.combined_id)

  if not cid_matches:
    sys.stderr.write('Failed to match combined id %s in row %s\n' % (de.combined_id, de))
    num_err_rows += 1
    continue

  source_id = cid_matches.group(1)
  table_id = cid_matches.group(2)
  nr = cid_matches.group(3)

  table = Table.objects.get(old_id = table_id)

  if table.old_source_id != de.source_id:
    sys.stderr.write('Returned table %s did not match old source id for %s\n' % (table, de))
    num_err_rows += 1
    continue

  de.source_table = table
  de.save()

sys.stdout.write('Linking completed.  %i error(s) encountered\n' % num_err_rows)

