#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

if __name__ == "__main__":
  infile = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  countries = set()

  for i, row in enumerate(reader):
    if i < 1:
      continue

    rdict = dict(zip(('country1_id', 'country2_id', 'dyad_id', 'country1', 'country2',), row))

    countries.add(rdict['country1'])
    countries.add(rdict['country2'])

  for c in countries:
    print(c)

