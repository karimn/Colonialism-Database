from colonialismdb.population.models import MainDataEntry, PopulationCondition, Occupation
from colonialismdb.sources.models import Table
from colonialismdb.common.admin import BaseSubmitAdmin, BaseMergeableCategoryAdmin
from django.contrib import admin

class MainDataEntryAdmin(BaseSubmitAdmin) :
  def change_view(self, request, object_id, extra_context=None):
    result = super(MainDataEntryAdmin, self).change_view(request, object_id, extra_context)

    if request.POST.has_key('_addanother'):
      request.session['reuse_values'] = { 'source' : request.POST['source'], 'location' : request.POST['location'], }

    return result

  def add_view(self, request, form_url = '', extra_context=None):
    if request.session.has_key('reuse_values'):
      request.GET = request.GET.copy()
      request.GET.update(request.session['reuse_values'])
      del request.session['reuse_values']

    result = super(MainDataEntryAdmin, self).add_view(request, form_url, extra_context)

    return result
  
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
        {'fields' : ['source', 'page_num', 'polity', 'iso', 'wb']}),

      ('Other Information', 
        {'fields' : ['remarks', ], 'classes' : ['collapse', ]}),
  ]

  radio_fields = { 'value_precision' : admin.HORIZONTAL, 'individ_fam' : admin.HORIZONTAL, 'population_gender' : admin.HORIZONTAL, 'value_unit' : admin.HORIZONTAL, }

  list_display = ('location', 'begin_date', 'end_date', 'active', 'submitted_by')
  ordering = ['begin_date']

  activate_perm = 'population.activate_main_data_entry'

class PopulationConditionAdmin(BaseMergeableCategoryAdmin) :
  activate_perm = 'population.activate_population_condition'
  merge_perm = 'population.merge_population_condition'

class OccupationAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'population.activate_occupation'
  merge_perm = 'population.merge_occupation'

admin.site.register(MainDataEntry, MainDataEntryAdmin)
admin.site.register(PopulationCondition, PopulationConditionAdmin)
admin.site.register(Occupation, OccupationAdmin)
