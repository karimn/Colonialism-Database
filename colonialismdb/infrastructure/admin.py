from colonialismdb.infrastructure.models import MainDataEntry
from colonialismdb.sources.models import Table, SpatialAreaUnit, Currency 
from colonialismdb.common.admin import BaseSubmitAdmin, BaseMergeableCategoryAdmin, BaseMainDataEntryAdmin
from django.contrib import admin

class MainDataEntryAdmin(BaseMainDataEntryAdmin) :
  fieldsets = [
      (None,
        {'fields' : ['active', 'submitted_by']}),

      ('Location Information', 
        {'fields' : ['location', 'original_location_name', 'alternate_location_name', 'spatial_area', 'spatial_area_unit']}),
      
      ('Date Range', 
        {'fields' : ['begin_date', 'end_date', 'circa']}),

      ('Currency',
        {'fields' : ['currency', 'currency_exchange_rate']}),

      ('Railroad',
        {'fields' : ['railroad_length', 'railroad_freight', 'railroad_revenue', 'railroad_expenditure']}),

      ('Road',
        {'fields' : ['road_length', ]}),

      ('Telegraph',
        {'fields' : ['telegraph_length', ]}),

      ('Source Information', 
        {'fields' : ['source', 'page_num', 'primary_source', 'polity', 'iso', 'wb']}),

      ('Other Information', 
        {'fields' : ['remarks', ], 'classes' : ['collapse', ]}),
  ]

  #radio_fields = { 'value_precision' : admin.HORIZONTAL, 'individ_fam' : admin.HORIZONTAL, 'population_gender' : admin.HORIZONTAL, 'value_unit' : admin.HORIZONTAL, }

  list_display = ('location', 'begin_date', 'end_date', 'active', 'submitted_by')
  ordering = ['begin_date']

  activate_perm = 'infrastructure.activate_maindataentry'

admin.site.register(MainDataEntry, MainDataEntryAdmin)
