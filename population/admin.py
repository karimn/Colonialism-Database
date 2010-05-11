from colonialismdb.population.models import Location, MainDataEntry
from django.contrib import admin

class MainDataEntryAdmin(admin.ModelAdmin) :
  fieldsets = [
      (None, {'fields' : ['begin_date', 'end_date', 'religion', 'race', 'ethnicity', 'ethnic_origin', 'age_start', 'age_end', 'remarks', 'population_condition'] }),
      ('Source Information', {'fields' : ['source_id', 'polity', 'wb']}),
      ('Location Information', {'fields' : ['location', 'original_location_name', 'alternate_location_name']}),
      ('Population Statistics', {'fields' : ['individuals_population_value', 'families_population_value', 'male_population_value', 'female_population_value', 'is_total']})
  ]

admin.site.register(Location)
admin.site.register(MainDataEntry, MainDataEntryAdmin)
