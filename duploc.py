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

  print("%i duplicates found\n" % len(loc_dict))

  for loc_name, locs in loc_dict.iteritems():
    try:
      print("Unique name: %s (%i duplicates)" % (loc_name, len(locs)))
      pks = []
      for loc in locs:
        print("\t* %s (politically in %s) (pk = %i)" % (loc, loc.politically_in, loc.pk))
        pks.append(loc.pk)
      print("pks: %s\n" % " ".join([unicode(i) for i in pks]))
      #raw_input()
    except UnicodeEncodeError:
      # Windows decode error workaround
      print("<UnicodeEncodeError Encountered, ignoring for now>")

