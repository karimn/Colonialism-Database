from colonialismdb.common import models
from django.contrib import admin
from reversion.admin import VersionAdmin
from reversion import revision

import reversion

class BaseSubmitAdmin(VersionAdmin) :
  @revision.create_on_success
  def activate(self, request, query_set):
    """ 
    We should have a concurrency problem here if more than one person are trying to activate entries at the same time.  
    We could use "SELECT FOR UPDATE ..." or the django-locking module, but I would rather wait for 
    http://code.djangoproject.com/ticket/2705 to be integrated into Django.
    """
    rows_activated = 0

    for entry in query_set:
      entry.activate()
      revision.user = request.user
      revision.comment = "Activation"

    if rows_activated > 0:
      self.message_user(request, '%i %s activated' % (rows_activated, 'entry' if rows_activated == 1 else 'entries'))

  activate.short_description = 'Activate'

  @revision.create_on_success
  def save_model(self, request, obj, form, change):
    if not change and obj.active == False:
      obj.submitted_by = request.user
      obj.save()
      revision.user = request.user
      revision.comment = "Submitted new data"
    else:
      obj.save()

  def get_actions(self, request):
    actions = super(BaseSubmitAdmin, self).get_actions(request)
    
    if not request.user.has_perm(self.__class__.activate_perm):
      del actions['activate']

    return actions

  def queryset(self, request):
    qs = super(BaseSubmitAdmin, self).queryset(request)

    if not request.user.has_perm(self.__class__.activate_perm):
      qs = qs.filter(submitted_by = request.user)

    return qs

  actions = ('activate', )
  readonly_fields = ('active', 'submitted_by')
  list_filter = ('active', 'submitted_by')

class BaseMergeableAdmin(VersionAdmin):
  #@revision.create_on_success
  def merge(self, request, query_set):
    """ 
    We should have a concurrency problem here if more than one person are trying to activate entries at the same time.  
    We could use "SELECT FOR UPDATE ..." or the django-locking module, but I would rather wait for 
    http://code.djangoproject.com/ticket/2705 to be integrated into Django.
    """
    rows_merged = 0

    if query_set.count < 2:
      # TODO Add error message
      return

    merge_into = query_set[0]

    for merge in query_set[1:]:
      with reversion.revision:
        merge.merge_into(merge_into)
        revision.user = request.user
        revision.comment = "Merged into %s" % merge_into
      rows_merged += 1

    for merge in query_set[1:]:
      with reversion.revision:
        merge.delete()
        revision.user = request.user
        revision.comment = "Deleted after merging"

    with reversion.revision:
      merge_into.save()
      revision.user = request.user
      revision.comment = "%i entries merged into this entry" % rows_merged

    if rows_merged > 0:
      self.message_user(request, '%i entries merged' % (rows_merged + 1))

  merge.short_description = 'Merge entries'

  def get_actions(self, request):
    actions = super(VersionAdmin, self).get_actions(request)

    if not request.user.has_perm(self.__class__.merge_perm):
      del actions['merge']

    return actions

  actions = ('merge', )

class PoliticalUnitAdmin(BaseSubmitAdmin, BaseMergeableAdmin):
  list_display = ('__unicode__', 'active', 'submitted_by')
  activate_perm = 'common.activate_polunit'
  merge_perm = 'common.merge_polunit'

  actions = BaseSubmitAdmin.actions + BaseMergeableAdmin.actions

  def get_actions(self, request):
    actions1 = BaseSubmitAdmin.get_actions(self, request)
    actions2 = BaseMergeableAdmin.get_actions(self, request)

    actions1.update(actions2)
    return actions1

class LocationAdmin(PoliticalUnitAdmin) :
  #list_display = ('__unicode__', 'active', 'submitted_by')
  exclude = ('full_name', )
  activate_perm = 'common.activate_location'
  merge_perm = 'common.merge_location'

class TemporalLocationAdmin(LocationAdmin):
  activate_perm = 'common.activate_temploc'
  merge_perm = 'common.merge_temploc'
  
class BaseCategoryAdmin(BaseSubmitAdmin, BaseMergeableAdmin):
  list_display = ('name', 'active', 'submitted_by')

class BaseMergeableCategoryAdmin(BaseCategoryAdmin, BaseMergeableAdmin):
  actions = BaseCategoryAdmin.actions + BaseMergeableAdmin.actions 

  def get_actions(self, request):
    actions1 = BaseCategoryAdmin.get_actions(self, request)
    actions2 = BaseMergeableAdmin.get_actions(self, request)

    actions1.update(actions2)
    return actions1

class ReligionAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_religion'
  merge_perm = 'common.merge_religion'

class RaceAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_race'
  merge_perm = 'common.merge_race'

class EthnicityAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_ethnicity'
  merge_perm = 'common.merge_ethnicity'
  
class EthnicOriginAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_ethnic_origin'
  merge_perm = 'common.merge_ethnic_origin'

class PoliticalUnitTypeAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_polunittype'
  merge_perm = 'common.merge_polunittype'

class LanguageAdmin(BaseMergeableCategoryAdmin):
  activate_perm = 'common.activate_language'
  merge_perm = 'common.merge_language'

admin.site.register(models.PoliticalUnit, PoliticalUnitAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.TemporalLocation, TemporalLocationAdmin)
admin.site.register(models.Religion, ReligionAdmin)
admin.site.register(models.Race, RaceAdmin)
admin.site.register(models.Ethnicity, EthnicityAdmin)
admin.site.register(models.EthnicOrigin, EthnicOriginAdmin)
admin.site.register(models.PoliticalUnitType, PoliticalUnitTypeAdmin)
admin.site.register(models.Language, LanguageAdmin)
