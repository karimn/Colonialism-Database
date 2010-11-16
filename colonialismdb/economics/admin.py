from colonialismdb.economics.models import AggregateTradeDataEntry, BilateralTradeDataEntry
from colonialismdb.sources.models import Table
from colonialismdb.common.admin import BaseSubmitAdmin, BaseMergeableCategoryAdmin, BaseMainDataEntryAdmin
from django.contrib import admin

class BaseTradeDataEntryAdmin(BaseMainDataEntryAdmin):
  radio_fields = { 'imports_value_unit' : admin.HORIZONTAL, 'exports_value_unit' : admin.HORIZONTAL }

class AggregateTradeDataEntryAdmin(BaseTradeDataEntryAdmin):
  fieldsets = [
      (None,
        {'fields' : ['active', 'submitted_by', 'datetime_created', ]}),

      ('Location Information', 
        {'fields' : ['location', 'original_location_name', 'alternate_location_name', ]}),
      
      ('Date Range', 
        {'fields' : ['begin_date', 'end_date', 'circa']}),

      ('Trade',
        {'fields' : ['imports', 'imports_value_unit', 'exports', 'exports_value_unit', 'currency', ]}),

      ('Source Information', 
        {'fields' : ['source', 'page_num', 'primary_source_obj', 'primary_source_text']}),

      ('Other Information', 
        {'fields' : ['remarks', ]}),
  ]

  activate_perm = 'economics.activate_aggtradedataentry'
  
class BilateralTradeDataEntryAdmin(BaseTradeDataEntryAdmin):
  fieldsets = [
      (None,
        {'fields' : ['active', 'submitted_by', 'datetime_created', ]}),

      ('Location Information', 
        {'fields' : ['location', 'original_location_name', 'alternate_location_name', 'trade_partner']}),
      
      ('Date Range', 
        {'fields' : ['begin_date', 'end_date', 'circa']}),

      ('Trade',
        {'fields' : ['imports', 'imports_value_unit', 'exports', 'exports_value_unit', 'imports_exchange_rate', 'exports_exchange_rate', 'gfd_exchange_rate', 'exchange_rate_scalar', 'currency',
                     'imports_weight', 'imports_weight_unit', 'exports_weight', 'exports_weight_unit', 'ppi']}),

      ('Source Information', 
        {'fields' : ['source', 'page_num', 'primary_source_obj', 'primary_source_text']}),

      ('Other Information', 
        {'fields' : ['remarks', ]}),
  ]

  autocomplete_fields = BaseMainDataEntryAdmin.autocomplete_fields 
  autocomplete_fields.update({ 'trade_partner' : ('name', 'autocomplete_label'), })

  activate_perm = 'economics.activate_bilatradedataentry'

  list_display = ('location', 'trade_partner', 'begin_date', 'end_date', 'active', 'submitted_by', 'datetime_created', )
  list_display_links = ('location', 'trade_partner', )

admin.site.register(AggregateTradeDataEntry, AggregateTradeDataEntryAdmin)
admin.site.register(BilateralTradeDataEntry, BilateralTradeDataEntryAdmin)
