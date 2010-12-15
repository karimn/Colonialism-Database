#!/usr/bin/python

import sys

from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location

if __name__ == "__main__":
  loc_dict = dict()
  
  for loc in Location.objects.all():
    loc_name = loc.name.lower()
    if loc_dict.has_key(loc_name):
      loc_dict[loc_name].append(loc)
    else:
      loc_dict[loc_name] = [loc]

  loc_dict = dict(filter(lambda x: len(x[1]) > 1, loc_dict.items()))

  for loc_name, locs in loc_dict.iteritems():
    print("Unique name: %s (%i duplicates)" % (loc_name, len(locs)))
    for loc in locs:
      print("\t* %s (politically in %s)" % (unicode(loc), unicode(loc.politically_in)))
    raw_input()

