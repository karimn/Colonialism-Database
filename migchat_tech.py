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
from django.db.models import Q

asia = Location.objects.get(Q(name = "Asia"), Q(geographically_in = None))
africa = Location.objects.get(Q(name = "Africa"), Q(geographically_in = None))
europe = Location.objects.get(Q(name = "Europe"), Q(geographically_in = None))
oceania = Location.objects.get(Q(name = "Oceania"), Q(geographically_in = None))
north_america = Location.objects.get(Q(name = "North America"), Q(geographically_in = None))
south_america = Location.objects.get(Q(name = "South America"), Q(geographically_in = None))
central_america = Location.objects.get(Q(name = "Central America"), Q(geographically_in = None))

continents = ((asia, Source.objects.get(pk = 162)), (africa, Source.objects.get(pk = 162)), (oceania, Source.objects.get(pk = 162)),
              (north_america, Source.objects.get(pk = 13)), (south_america, Source.objects.get(pk = 13)), (central_america, Source.objects.get(pk = 13)),
              (europe, Source.objects.get(pk = 50)))

ship_types = ("all", "motor", "sail", "steam", "steammotor")

metadata_col = set(('submitted_by', 'begin_date', 'source', 'location', 'primary_source_obj', 'end_date', 'active'))

if __name__ == "__main__":
  infile = sys.argv[1]
  reader = csv.reader(migtools.UTF8Recoder(open(infile, "r"), migtools.STRING_ENCODING), delimiter='\t', quotechar = '"')

  num_err_rows = 0
  num_excluded = 0
  num_mig = 0
  num_locs = 0

  src = Source.objects.get(pk = 3397)

  locations_not_found = set() 

  start_with = 1 
  
  if len(sys.argv) > 2:
    start_with = int(sys.argv[2])

  for i, row in enumerate(reader):
    if (i < start_with):
      continue


    rdict = dict(zip(("location", "year", 
                      "air_passenger_km", "air_passenger_km_value_unit", "air_cargo_ton_km", "air_cargo_ton_km_value_unit", 
                      "postal_num_items", "postal_num_items_value_unit",
                      "railroad_length", "railroad_length_unit", 
                      "railroad_num_passengers", "railroad_num_passengers_value_unit", 
                      "railroad_passenger_km_value_unit", "railroad_passenger_km",
                      "railroad_freight", "railroad_freight_unit", 
                      "railroad_freight_ton_km", "railroad_freight_ton_km_value_unit",
                      "ships_all_num", "ships_all_num_value_unit", "ships_motor_num", "ships_motor_num_value_unit", 
                      "ships_sail_num", "ships_sail_num_value_unit", "ships_steam_num", "ships_steam_num_value_unit", 
                      "ships_steammotor_num", "ships_steammotor_num_vaue_unit",
                      "ships_all_ton", "ships_all_ton_value_unit", "ships_motor_ton", "ships_motor_ton_value_unit", "ships_sail_ton",
                      "ships_sail_ton_value_unit", "ships_steam_ton", "ships_steam_ton_value_unit", 
                      "ships_steammotor_ton", "ships_steammotor_ton_value_unit",
                      "telegraph_num_sent", "telegraph_num_sent_value_unit", "num_motor_vehicles", "num_motor_vehicles_value_unit"), row[2:]))

    found = False
    for cont, prim_src in continents:
#      locs = cont.get_geographic_sub_locations().filter(Q(name__iexact = rdict["location"]), Q(politically_in = None))[:1]
      locs = cont.geographically_contains.filter(Q(name__iexact = rdict["location"]), Q(politically_in = None))[:1]
      if len(locs) > 0:
        found = True
        rdict["location"] = locs[0]
        rdict["primary_source_obj"] = prim_src
        break

    if not found:
      sys.stderr.write("Location not found (%i): %s\n" % (i, rdict["location"]))
      locations_not_found.add(rdict["location"])
      num_err_rows += 1
      continue

    rdict["begin_date"] = datetime.date(int(float(rdict["year"])), 1, 1)
    rdict["end_date"] = datetime.date(int(float(rdict["year"])), 12, 31)
    del rdict["year"]

    rdict["active"] = True
    rdict["submitted_by"] = migtools.mig_user

    rdict["source"] = src

    rdict = dict(map(migtools.strip_rdict, rdict.items())) # Remove blank strings
    rdict = dict(filter(lambda x: x[1], rdict.items())) # removing null values
    
    if rdict.has_key("railroad_length"):
      rdict["railroad_length_unit"] = LengthUnit.objects.get(name__iexact = rdict["railroad_length_unit"])
    elif rdict.has_key("railroad_length_unit"):
      del rdict["railroad_length_unit"]

    if rdict.has_key("railroad_passenger_km"):
      rdict["railroad_passenger_km_value_unit"] = rdict["railroad_passenger_km_value_unit"].split()[0] + "s"
    else:
      del rdict["railroad_passenger_km_value_unit"] 

    if rdict.has_key("air_passenger_km"):
      rdict["air_passenger_km_value_unit"] = rdict["air_passenger_km_value_unit"].split()[0] + "s"
    else:
      del rdict["air_passenger_km_value_unit"]

    if rdict.has_key("air_cargo_ton_km"):
      rdict["air_cargo_ton_km_value_unit"] = rdict["air_cargo_ton_km_value_unit"].split()[0] + "s"
    else:
      del rdict["air_cargo_ton_km_value_unit"]

    if (not rdict.has_key("railroad_num_passengers")) and (rdict.has_key("railroad_num_passengers_value_unit")):
      del rdict["railroad_num_passengers_value_unit"]  
      
    if rdict.has_key("railroad_freight"):
      (rdict["railroad_freight_value_unit"], weight_unit) = rdict["railroad_freight_unit"].split(' ', 1)
      rdict["railroad_freight_value_unit"] += "s"
      rdict["railroad_freight_unit"] = WeightUnit.objects.get(name__iexact = weight_unit)
    else:
      del rdict["railroad_freight_unit"] 

    if rdict.has_key("railroad_freight_ton_km"):
      rdict["railroad_freight_ton_km_value_unit"] = rdict["railroad_freight_ton_km_value_unit"].split()[0] + "s"
    else:
      del rdict["railroad_freight_ton_km_value_unit"] 

    if rdict.has_key("num_motor_vehicles"):
      rdict["motor_vehicles_type"] = MotorVehicleType.objects.get(name__iexact = "Commercial")
    elif rdict.has_key("num_motor_vehicles_value_unit"):
      del rdict["num_motor_vehicles_value_unit"]

    if (not rdict.has_key("postal_num_items")) and (rdict.has_key("postal_num_items_value_unit")):
      del rdict["postal_num_items_value_unit"]

    for var in ("num", "ton"):
      for ship_type in ship_types:
        if rdict.has_key("ships_%s_%s_value_unit" % (ship_type, var)):
          if rdict.has_key("ships_%s_%s" % (ship_type, var)):
            rdict["ships_%s_%s_value_unit" % (ship_type, var)] = rdict["ships_%s_%s_value_unit" % (ship_type, var)].split()[0] + "s"
          else:
            del rdict["ships_%s_%s_value_unit" % (ship_type, var)]

    if (not rdict.has_key("telegraph_num_sent")) and (rdict.has_key("telegraph_num_sent_value_unit")):
      del rdict["telegraph_num_sent_value_unit"]

    if len(set(rdict.keys()) - metadata_col) == 0:
      sys.stdout.write("[%i] Excluding empty row: %s\n" % (i, row))
      num_excluded += 1
      continue

    try:
      entry = MainDataEntry(**rdict)
      entry.save()
      num_mig += 1
      sys.stdout.write("[%i] %s\n" % (i, entry))
    except (ValueError, DatabaseError, ValidationError) as e:
      sys.stderr.write('[%i] Failed to save data row: %s\n' % (i, e))
      num_err_rows += 1

  print 'Migration complete. %i rows migrated, %i rows excluded, %i locations not found, and %i row errors encountered and ignored' % (num_mig, num_excluded, len(locations_not_found), num_err_rows)
  if len(locations_not_found) > 0:
    print("Locations not found: %s" % (", ".join(locations_not_found)))
