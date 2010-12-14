#!/usr/bin/python

import sys

from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location
from colonialismdb.common.admin import merge

if __name__ == "__main__":
  if len(sys.argv) > 1:
    loc_name = sys.argv[1]

    merge_into = Location.get_toplevel().filter(name__iexact = loc_name)[0]

    if Location.get_toplevel().filter(name__iexact = loc_name).count() > 1:
      for l in Location.get_toplevel().filter(name__iexact = loc_name)[1:]:
        l.merge_into(merge_into)
        l.save()
      for l in Location.get_toplevel().filter(name__iexact = loc_name)[1:]:
        l.delete()
      merge_into.save()

    if len(sys.argv) > 3:
      if sys.argv[2] == "pk":
        put_in_loc = Location.objects.get(pk = sys.argv[3])
      else:
        put_in_loc = Location.get_toplevel().get(name__iexact = sys.argv[3])
      merge_into.geographicall_in = put_in_loc
      merge_into.save()


