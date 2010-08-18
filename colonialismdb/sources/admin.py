from colonialismdb.sources.models import Source, Table, SourceType, SourceSubject, DigitizationPriority, SourceFile
from colonialismdb.common.admin import BaseSubmitStackedInline, BaseSubmitTabularInline, BaseSubmitAdmin, BaseMergeableCategoryAdmin
from colonialismdb import population
from django.contrib import admin

class TableInline(BaseSubmitTabularInline):
  model = Table
  fields = ('name', 'original_name', 'nr', 'begin_page', 'end_page')
  fk_name = 'source'
  extra = 0

  activate_perm = 'sources.activate_table'

class PopulationDataInline(BaseSubmitTabularInline):
  model = population.models.MainDataEntry
  fields = ('location', 'begin_date', 'end_date', )
  #exclude = ('old_source_id', 'old_combined_id')
  readonly_fields = ('active', 'submitted_by')
  list_display_links = ('location', )

  fk_name = 'source'
  extra = 0

  activate_perm = 'population.activate_main_data_entry'

class SourceFileInline(BaseSubmitTabularInline):
  model = SourceFile
  max_num = None
  extra = 0

  activate_perm = 'sources.activate_sourcefile'

class SourceAdmin(BaseSubmitAdmin) :
  exclude = ('old_id', )

  list_display = ('author', 'editor', 'title', 'volume', 'year', 'active', 'submitted_by')
  list_display_links = ('author', 'editor', 'title')
  search_fields = ('title', 'original_title')
  ordering = ['author']

  inlines = [ SourceFileInline, TableInline, PopulationDataInline ]

  activate_perm = 'sources.activate_source'

class TableAdmin(BaseSubmitAdmin):
  exclude = ('old_id', 'old_source_id')

  list_display = ('name', 'nr', 'active', 'submitted_by')
  list_display_links = ('name', 'nr')
  search_fields = ('name', 'original_name')
  ordering = ['source']

  inlines = [ SourceFileInline, PopulationDataInline, ]

  activate_perm = 'sources.activate_table'

class SourceTypeAdmin(BaseMergeableCategoryAdmin) :
  activate_perm = 'sources.activate_sourcetype'
  merge_perm = 'sources.merge_sourcetype'

class SourceSubjectAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'sources.activate_sourcesubject'
  merge_perm = 'sources.merge_sourcesubject'

class DigitizationPriorityAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'sources.activate_digipriority'
  merge_perm = 'sources.merge_digipriority'

admin.site.register(Source, SourceAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(SourceSubject, SourceSubjectAdmin)
admin.site.register(DigitizationPriority, DigitizationPriorityAdmin)
