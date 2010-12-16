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

  quit = False

  for loc_name, locs in loc_dict.iteritems():
    try:
      print("Unique name: %s (%i duplicates)" % (loc_name, len(locs)))
      pks = []
      for i, loc in enumerate(locs):
        loc_data = [] #loc.get_all_data()
        print("\t%i) %s (politically in %s) (pk = %i)" % (i+1, loc, loc.politically_in, loc.pk))
        pks.append(loc.pk)
      print("pks: %s\n" % " ".join([unicode(i) for i in pks]))
      sys.stdout.write("Merge into (enter row number, 's' to skip, or 'q' to quit): ")
      while True:
        action = raw_input()
        if action == 's':
          break
        elif action == 'q':
          quit = True
          break
        elif action.isdigit() and (int(action) >= 1) and (int(action) <= len(locs)):
          sys.stdout.write("Merging")
          merge_into = locs[int(action) - 1]
          sys.stdout.write("all into '%s (pk = %i)'..." % (unicode(merge_into), merge_into.pk))
          to_merge = filter(lambda x: x.pk != merge_into.pk, locs)
          for l in to_merge:
            l.merge_into(merge_into)
          for l in to_merge:
            l.delete()
          try:
            merge_into.save()
          except Location.DoesNotExist:
            pass

          sys.stdout.write("...completed\n") #len(merge_into.get_all_data()))
          break
      if quit:
        break

    except UnicodeEncodeError:
      # Windows decode error workaround
      print("<UnicodeEncodeError Encountered, ignoring for now>")

