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
        {'fields' : ['railroad_revenue', 'railroad_expenditure', 'railroad_length', 'railroad_length_unit', 'railroad_num_passengers', 'railroad_passenger_km', 'railroad_freight', 'railroad_freight_unit', ]}),

      ('Road',
        {'fields' : ['road_revenue', 'road_expenditure', 'road_length', 'road_length_unit', 'num_motor_vehicles', 'motor_vehicles_type', ]}),

      ('Telephones/Telegraph',
        {'fields' : ['num_telephones', 'telegraph_length', 'telegraph_length_unit', 'telegraph_num_stations', 'telegraph_num_sent', ]}),

      ('Postal',
        {'fields' : ['postal_revenue', 'postal_expenditure', 'postal_num_stations', 'postal_num_items', 'postal_items_type', 'postal_num_boxes', 'postal_num_staff',  ]}),

      ('Merchant Ships',
        {'fields' : ['merchant_ships_num', 'merchant_ships_type', 'merchant_ships_cargo', 'merchant_ships_cargo_unit', ]}),

      ('Aviation',
        {'fields' : ['air_cargo', 'air_cargo_unit', 'air_passenger_km', ]}),

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
