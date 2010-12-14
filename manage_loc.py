#!/usr/bin/python

import sys

from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location
from colonialismdb.common.admin import merge

mig_user = User.objects.get(username = 'karim')

if __name__ == "__main__":
  if len(sys.argv) > 1:
    loc_name = sys.argv[1]

    for l in Location.get_toplevel().filter(name__iexact = loc_name):
      print("%s (politically in %s)" % (l.name, l.politically_in))
  else:
    loc_dict = dict()
    for l in Location.get_toplevel():
      l_name = l.name.lower()
      if loc_dict.has_key(l_name):
        loc_dict[l_name].append(l)
      else:
        loc_dict[l_name] = [l,]

    for l_name, l_list in loc_dict.iteritems():
      if len(l_list) > 1:
        print("%s : %i" % (l_name, len(l_list)))


