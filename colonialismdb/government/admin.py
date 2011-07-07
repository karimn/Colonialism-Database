from colonialismdb.government.models import MainDataEntry, RevenueType, ExpenditureType, MoneySupplyType, MilitaryType, OfficialsType
from colonialismdb.common.models import SpatialAreaUnit, Currency
from colonialismdb.sources.models import Table 
from colonialismdb.common.admin import BaseSubmitAdmin, BaseMergeableCategoryAdmin, BaseMainDataEntryAdmin
from django.contrib import admin

class MainDataEntryAdmin(BaseMainDataEntryAdmin) :
  fieldsets = [
      (None,
        {'fields' : ['active', 'submitted_by', 'datetime_created', ]}),

      ('Location Information', 
        {'fields' : ['location', 'original_location_name', 'alternate_location_name', 'spatial_area', 'spatial_area_unit', 'spatial_page_num', ]}),
      
      ('Date Range', 
        {'fields' : ['begin_date', 'end_date', 'circa']}),

      ('Currency',
        {'fields' : ['currency', 'currency_exchange_rate']}),

      ('Expenditure',
        {'fields' : ['expenditure', 'expenditure_type']}),

      ('Revenue',
        {'fields' : ['revenue', 'revenue_type']}),

      ('Public Debt',
        {'fields' : ['public_debt', 'public_debt_type']}),

      ('Personnel',
        {'fields' : ['military', 'military_type', 'military_page_num', 'officials', 'officials_type']}),

      ('Source Information', 
        {'fields' : ['source', 'page_num', 'primary_source_obj', 'primary_source_text']}),

      ('Other Information', 
        {'fields' : ['remarks', ]}),
  ]

  #radio_fields = { 'value_precision' : admin.HORIZONTAL, 'individ_fam' : admin.HORIZONTAL, 'population_gender' : admin.HORIZONTAL, 'value_unit' : admin.HORIZONTAL, }

  activate_perm = 'government.activate_maindataentry'
  reuse_fields = BaseMainDataEntryAdmin.reuse_fields + ('spatial_area_unit', 'spatial_page_num',)

class SpatialAreaUnitAdmin(BaseMergeableCategoryAdmin) :
  activate_perm = 'government.activate_spareaunit'
  merge_perm = 'government.merge_spareaunit'

class CurrencyAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'government.activate_currency'
  merge_perm = 'government.merge_currency'

class RevenueTypeAdmin(BaseMergeableCategoryAdmin):
    activate_perm = 'government.activate_revenuetype'
    merge_perm = 'government.merge_revenuetype'

class ExpenditureTypeAdmin(BaseMergeableCategoryAdmin):
    activate_perm = 'government.activate_expendituretype'
    merge_perm = 'government.merge_expendituretype'
    
class MoneySupplyTypeAdmin(BaseMergeableCategoryAdmin):
    activate_perm = 'government.activate_moneysupplytype'
    merge_perm = 'government.merge_moneysupplytype'

class MilitaryTypeAdmin(BaseMergeableCategoryAdmin):
    activate_perm = 'government.activate_militarytype'
    merge_perm = 'government.merge_militarytype'

class OfficialsTypeAdmin(BaseMergeableCategoryAdmin):
    activate_perm = 'government.activate_officialstype'
    merge_perm = 'government.merge_officialstype'
    
admin.site.register(MainDataEntry, MainDataEntryAdmin)
admin.site.register(SpatialAreaUnit, SpatialAreaUnitAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(RevenueType, RevenueTypeAdmin)
admin.site.register(ExpenditureType, ExpenditureTypeAdmin)
admin.site.register(MoneySupplyType, MoneySupplyTypeAdmin)
admin.site.register(MilitaryType, MilitaryTypeAdmin)
admin.site.register(OfficialsType, OfficialsTypeAdmin)
