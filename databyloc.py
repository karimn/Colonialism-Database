#!/usr/bin/python

import sys

from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location
from colonialismdb.sources.models import BaseSourceObject
from colonialismdb.population.models import MainDataEntry as PopDataEntry

def print_data_sources(loc_pks, print_loc_name = True, indent = 0):
    for loc_pk in loc_pks:
      loc = Location.objects.get(pk = loc_pk)
      loc_data = loc.get_all_data()
      if print_loc_name:
        sys.stdout.write("%sLocation: %s\n" % ('\t' * indent, loc))
      sys.stdout.write("%sNum Data Entries = %i\n" % ('\t' * (indent + 1), len(loc_data)))
      if len(loc_data) > 0:
        data_pks = [data.source.pk for data in loc_data]
        data_srcs = BaseSourceObject.objects.filter(pk__in = data_pks).distinct()
        sys.stdout.write("%sSources:\n" % ('\t' * (indent + 1)))
        for data_src in data_srcs:
          sys.stdout.write("%s%s (pk = %i)\n" % ('\t' * (indent + 2), data_src, data_src.pk))
        sys.stdout.write("\n")

if __name__ == "__main__":
  if len(sys.argv) > 1:
    print_data_sources(sys.argv[1:])
    
