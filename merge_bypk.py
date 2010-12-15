#!/usr/bin/python

import sys

from colonialismdb.common.models import Location

if __name__ == "__main__":
  if len(sys.argv) > 2:
    merge_into_pk = sys.argv[1]
    to_merge_pks = sys.argv[2:]

    merge_into = Location.objects.get(pk = merge_into_pk)
    to_merge = Location.objects.filter(pk__in = to_merge_pks)

    for l in to_merge:
      l.merge_into(merge_into)
      l.save()
    for l in to_merge:
      l.delete()
  
    merge_into.save()
