from colonialismdb.population.models import MainDataEntry, PopulationCondition, Occupation
from colonialismdb.common.admin import BaseSubmitAdmin, BaseCategoryAdmin
from django.contrib import admin

class MainDataEntryAdmin(BaseSubmitAdmin) :
  fieldsets = [
      (None,
        {'fields' : ['active', 'submitted_by']}),

      ('Location Information', 
        {'fields' : ['location', 'original_location_name', 'alternate_location_name']}),
      
      ('Date Range', 
        {'fields' : ['begin_date', 'end_date', 'circa']}),

      ('Population Characteristics', 
        {'fields' : ['religion', 'race', 'ethnicity', 'ethnic_origin', 'age_start', 'age_end', 'population_condition', 'occupation']}),

      ('Population Statistics', 
        {'fields' : ['individ_fam', 'population_gender', 'population_value', 'value_unit', 'is_total', 'value_precision']}),

      ('Source Information', 
        {'fields' : ['source_id', 'combined_id', 'page_num', 'polity', 'iso', 'wb']}),

      ('Other Information', 
        {'fields' : ['remarks', ], 'classes' : ['collapse', ]}),
  ]

  list_display = ('location', 'begin_date', 'end_date', 'active', 'submitted_by')
  ordering = ['begin_date']

  activate_perm = 'population.activate_main_data_entry'

class PopulationConditionAdmin(BaseCategoryAdmin) :
  activate_perm = 'population.activate_population_condition'

class OccupationAdmin(BaseCategoryAdmin):
  activate_perm = 'population.activate_occupation'

admin.site.register(MainDataEntry, MainDataEntryAdmin)
admin.site.register(PopulationCondition, PopulationConditionAdmin)
admin.site.register(Occupation, OccupationAdmin)
