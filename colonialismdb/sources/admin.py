from colonialismdb.sources.models import Source, Table, SourceType, SourceSubject, DigitizationPriority
from colonialismdb.common.admin import BaseSubmitAdmin, BaseCategoryAdmin
from django.contrib import admin

class TableInline(admin.TabularInline):
  model = Table

class SourceAdmin(BaseSubmitAdmin) :
  exclude = ('old_id', )

  list_display = ('author', 'editor', 'title', 'volume', 'year', 'active', 'submitted_by')
  list_display_links = ('author', 'editor', 'title')
  ordering = ['author']

  inlines = [ TableInline, ]

  activate_perm = 'sources.activate_source'

class TableAdmin(BaseSubmitAdmin):
  exclude = ('old_id', 'old_source_id')

  list_display = ('name', 'nr', 'active', 'submitted_by')
  list_display_links = ('name', 'nr')
  ordering = ['source']

  activate_perm = 'sources.activate_table'

class SourceTypeAdmin(BaseCategoryAdmin) :
  activate_perm = 'sources.activate_sourcetype'

class SourceSubjectAdmin(BaseCategoryAdmin):
  activate_perm = 'sources.activate_sourcesubject'

class DigitizationPriorityAdmin(BaseCategoryAdmin):
  activate_perm = 'sources.activate_digipriority'

admin.site.register(Source, SourceAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(SourceSubject, SourceSubjectAdmin)
admin.site.register(DigitizationPriority, DigitizationPriorityAdmin)
