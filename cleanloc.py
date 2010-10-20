#!/usr/bin/python

from django.db import transaction
from django.contrib.auth.models import User

from colonialismdb.common.models import PoliticalUnit, Location

mig_user = User.objects.get(username = 'karim')

def print_loc(query):
  for l in query:
    print("'%s', '%s', '%s', %s, %s" % (l.name, l.geographically_in, l.politically_in, l.geo_features, l.unit_type.count()))

@transaction.commit_manually
def cleanup_turkey():
  pass

if __name__ == "__main__":
  pass

