
#!/usr/bin/python

import csv
import sys
import re
import datetime
import functools

import migtools

from django.contrib.auth.models import User

from colonialismdb.common.models import BaseGeo, Location, TemporalLocation

mig_user = User.objects.get(username = 'karim')

if __name__ == "__main__":
  infile = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  num_errors = 0

  for i, row in enumerate(reader):
    if i == 0:
      continue

    rdict = dict(zip(("ft_id", "geom", "type", "sovern_power", "name", "name_1", "begin_date", "end_date", "preced", "followed", "place", "country", "country_1", "continent"), row[2:]))

    geo_features = None

    try:
      geo_features = BaseGeo.objects.get(ft_id = rdict["ft_id"])
    except BaseGeo.DoesNotExist:
      num_errors += 1
      sys.stderr.write("Failed to find FT ID %s\n" % rdict["ft_id"])
      continue

    top_obj = None
    #cont_obj = None
    base_loc_obj = None
    name = rdict["name"]
    continent = rdict["continent"]
    country1 = rdict["country"]
    country2 = rdict["country_1"]

    if name == country1:
      country1 = None
      country2 = None

    cont_matches = Location.objects.filter(name__iexact = continent).filter(geographically_in = None)

    if cont_matches.count() == 0:
      top_obj = Location(name = continent, submitted_by = mig_user, active = True, locked = True)
      top_obj.save()
    else:
      top_obj = cont_matches[0]

    for country in (country2, country1):
      if country:
        country_matches = top_obj.get_geographic_sub_locations(include_self = False).filter(name__iexact = country)

        if country_matches.count() == 0:
          top_obj = Location(name = country, geographically_in = top_obj, submitted_by = mig_user, active = True, locked = True)
          top_obj.save()
        else:
          top_obj = country_matches[0]

    loc_matches = top_obj.get_geographic_sub_locations(include_self = False).filter(name__iexact = name)

    if loc_matches.count() == 0:
      top_obj = Location(name = name, geographically_in = top_obj, submitted_by = mig_user, active = True, locked = True)
      top_obj.save()
    else:
      top_obj = loc_matches[0]

    begin_date = datetime.date(int(rdict["begin_date"]),1,1)
    end_date = datetime.date(int(rdict["end_date"]),12,31) if rdict["end_date"] and (rdict["end_date"] != "Present") else None

    if TemporalLocation.objects.filter(name__iexact = name).filter(temporal_is = top_obj).filter(begin_date = begin_date).filter(end_date = end_date).filter(geo_features = geo_features).count() > 0:
      sys.stdout.write("Entry already exists\n")
      continue

    temp_loc_obj = TemporalLocation(name = name, temporal_is = top_obj, begin_date = begin_date, end_date = end_date, geo_features = geo_features,
                                    submitted_by = mig_user, active = True, locked = True)
    temp_loc_obj.save()

  sys.stdout.write("Script completed.  %i error(s) encountered\n" % num_errors)

