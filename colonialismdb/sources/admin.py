from colonialismdb.sources.models import Source, SourceType, SourceSubject, DigitizationPriority
from colonialismdb.common.admin import BaseSubmitAdmin, BaseCategoryAdmin
from django.contrib import admin

class SourceAdmin(BaseSubmitAdmin) :
  exclude = ('old_id', )

  list_display = ('author', 'editor', 'title', 'volume', 'year', 'active', 'submitted_by')
  list_display_links = ('author', 'editor', 'title')
  ordering = ['author']

  activate_perm = 'sources.activate_source'

class SourceTypeAdmin(BaseCategoryAdmin) :
  activate_perm = 'sources.activate_sourcetype'

class SourceSubjectAdmin(BaseCategoryAdmin):
  activate_perm = 'sources.activate_sourcesubject'

class DigitizationPriorityAdmin(BaseCategoryAdmin):
  activate_perm = 'sources.activate_digipriority'

admin.site.register(Source, SourceAdmin)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(SourceSubject, SourceSubjectAdmin)
admin.site.register(DigitizationPriority, DigitizationPriorityAdmin)
