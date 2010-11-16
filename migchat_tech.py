#!/usr/bin/python

import csv
import datetime
import sys
import re
import functools

import migtools

from colonialismdb.infrastructure.models import MainDataEntry, MotorVehicleType
from colonialismdb.common.models import Location, LengthUnit, WeightUnit
from colonialismdb.sources.models import Source, Table

from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

if __name__ == "__main__":
  infile = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter=',', quotechar = '"')

  num_err_rows = 0
  num_mig = 0
  num_locs = 0

  src = None
  
  if len(sys.argv) > 2:
    src = Source.objects.get(pk = int(sys.argv[2]))
  else:
    src = Source.objects.get(pk = 3397)

  for i, row in enumerate(reader):
    if i < 1:
      continue

    rdict = dict(zip(("location", "year", "air_passenger_km", "air_cargo_ton_km", "postal_num_items", "railroad_length", "railroad_num_passengers",
                      "railroad_passenger_km", "railroad_freight", "railroad_freight_ton_km", "ships_num_all", "ships_motor_num", 
                      "ships_sail_num", "ships_steam_num", "ships_steammotor_num", "telegraph_num_sent", "num_motor_vehicles"), row))

    rdict["railroad_length_unit"] = LengthUnit.objects.get(name__iexact = "Kilometers")
    rdict["railroad_num_passengers_value_unit"] = "thousands"
    rdict["railroad_freight_unit"] = WeightUnit.objects.get(name__iexact = "Tons")
    rdict["motor_vehicles_type"] = MotorVehicleType.objects.get(name__iexact = "Commercial")

    locs = Location.objects.filter(name__iexact = rdict["location"]).filter(politically_in = None)[:1]
    if len(locs) == 0:
      rdict["location"] = Location(name = rdict["location"], submitted_by = migtools.mig_user)
      rdict["location"].save()
      num_locs += 1
    else:
      rdict["location"] = locs[0]

    rdict["begin_date"] = datetime.date(int(rdict["year"]), 1, 1)
    rdict["end_date"] = datetime.date(int(rdict["year"]), 12, 31)
    del rdict["year"]

    rdict["active"] = True
    rdict["submitted_by"] = migtools.mig_user

    rdict["source"] = src
    
    try:
      entry = MainDataEntry(**rdict)
      entry.save()
      num_mig += 1
      sys.stdout.write("[%i]\n" % i)
    except (ValueError, DatabaseError, ValidationError) as e:
      sys.stderr.write('Failed to save data row (%i): %s\n' % (i, e))
      num_err_rows += 1

  print 'Migration complete. %i rows migrated, %i locations created, and %i row errors encountered and ignored' % (num_mig, num_locs, num_err_rows)
