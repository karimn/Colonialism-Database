from colonialismdb.infrastructure.models import MainDataEntry, MotorVehicleType, PostalItemType, MerchantShipType
from colonialismdb.common.models import SpatialAreaUnit, Currency
from colonialismdb.sources.models import Table
from colonialismdb.common.admin import BaseSubmitAdmin, BaseMergeableCategoryAdmin, BaseMainDataEntryAdmin
from django.contrib import admin

class MainDataEntryAdmin(BaseMainDataEntryAdmin) :
  fieldsets = [
      (None,
        {'fields' : ['active', 'submitted_by', 'datetime_created', ]}),

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

  activate_perm = 'infrastructure.activate_maindataentry'

class MotorVehicleTypeAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'infrastructure.activate_mvehicletype'
  merge_perm = 'infrastructure.merge_mvehicletype'

class PostalItemTypeAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'infrastructure.activate_postalitemtype'
  merge_perm = 'infrastructure.merge_postalitemtype'

class MerchantShipTypeAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'infrastructure.activate_mshiptype'
  merge_perm = 'infrastructure.merge_mshiptype'

admin.site.register(MainDataEntry, MainDataEntryAdmin)
admin.site.register(MotorVehicleType, MotorVehicleTypeAdmin)
admin.site.register(PostalItemType, PostalItemTypeAdmin)
admin.site.register(MerchantShipType, MerchantShipTypeAdmin)
