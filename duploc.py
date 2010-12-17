#!/usr/bin/python

import sys
import pickle

from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location

if __name__ == "__main__":
  loc_dict = dict()
  
  for loc in Location.objects.all():
    loc_name = loc.name.lower()
    if loc_dict.has_key(loc_name):
      loc_dict[loc_name].append(loc.pk)
    else:
      loc_dict[loc_name] = [loc.pk]

  loc_dict = dict(filter(lambda x: len(x[1]) > 1, loc_dict.items()))

  print("%i duplicates found\n" % len(loc_dict))

  quit = False
  skipped = set()

  try:
    skipped_file = open("duploc.skip", "r")
    skipped = pickle.load(skipped_file)
    skipped_file.close()
  except IOError:
    pass

  try:
    for loc_name, locs in loc_dict.iteritems():
      try:
        if loc_name in skipped:
          continue
        print("Unique name: %s (%i duplicates)" % (loc_name, len(locs)))
        for i, loc_pk in enumerate(locs):
          loc = Location.objects.get(pk = loc_pk)
          #loc_data = loc.get_all_data()
          #print("\t%i) %s (politically in %s) (pk = %i) (data entries = %i)" % (i+1, loc, loc.politically_in, loc.pk, len(loc_data)))
          print("\t%i) %s (politically in %s) (pk = %i)" % (i+1, loc, loc.politically_in, loc.pk))
        print("pks: %s\n" % " ".join([unicode(i) for i in locs]))
        while True:
          sys.stdout.write("Merge into (enter row number, 's' to skip, or 'q' to quit): ")
          action = raw_input()
          if action == 's':
            skipped.add(loc_name)
            break
          elif action == 'q':
            quit = True
            break
          elif action.isdigit() and (int(action) >= 1) and (int(action) <= len(locs)):
            sys.stdout.write("Merging ")
            merge_into = Location.objects.get(pk = locs[int(action) - 1])
            sys.stdout.write("all into '%s' (pk = %i)..." % (unicode(merge_into), merge_into.pk))
            to_merge_pks = filter(lambda x: x != merge_into.pk, locs)
            to_merge = map(lambda x: Location.objects.get(pk = x), to_merge_pks)
            for l in to_merge:
              l.merge_into(merge_into)
            for l in to_merge:
              if l.is_geo_ancestor_of(merge_into):
                sys.stdout.write("\n*** Attempted to delete an ancestor of the location to merge to--ignoring\n")
              else:
                l.delete()
            try:
              merge_into.save()
            except Location.DoesNotExist:
              sys.stdout.write("\n*** Location not found exception raised on saving location to merge to--ignoring\n")
            #merge_into_data = merge_into.get_all_data()
            #sys.stdout.write("...done (data entries %i)\n\n" % len(merge_into_data)) #len(merge_into.get_all_data()))
            sys.stdout.write("...done\n\n") 
            break
        if quit:
          break
      except UnicodeEncodeError:
        # Windows decode error workaround
        print("<UnicodeEncodeError Encountered, ignoring for now>")
  finally:
    skipped_file = open("duploc.skip", "w")
    pickle.dump(skipped, skipped_file)
    skipped_file.close()

