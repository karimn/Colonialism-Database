#!/usr/bin/python

from django.db import transaction
from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location
from colonialismdb.common.admin import merge

mig_user = User.objects.get(username = 'karim')

def print_loc(query):
  for l in query:
    print("'%s', '%s', '%s', %s, %s" % (l.name, l.geographically_in, l.politically_in, l.geo_features, l.unit_type.count()))

@transaction.commit_manually
def cleanup_turkey():
  merge_into = Location.objects.filter(name__iexact = "Turkey").filter(geographically_in = None).filter(politically_in = None)[0]
  merge(merge_into, Location.objects.filter(name__iexact = "Turkey").filter(geographically_in = None).filter(politically_in = None)[1:])
  transaction.commit()

if __name__ == "__main__":
  pass

