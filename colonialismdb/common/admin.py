from colonialismdb.common import models
from django.contrib import admin
from reversion.admin import VersionAdmin
from reversion import revision

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

class PoliticalUnitAdmin(BaseSubmitAdmin):
  list_display = ('__unicode__', 'active', 'submitted_by')
  activate_perm = 'common.activate_polunit'

class LocationAdmin(BaseSubmitAdmin) :
  list_display = ('__unicode__', 'active', 'submitted_by')
  exclude = ('full_name', )
  activate_perm = 'common.activate_location'

class TemporalLocationAdmin(LocationAdmin) :
  activate_perm = 'common.activate_temploc'
  
class BaseCategoryAdmin(BaseSubmitAdmin):
  list_display = ('name', 'active', 'submitted_by')

class ReligionAdmin(BaseCategoryAdmin) :
  activate_perm = 'common.activate_religion'

class RaceAdmin(BaseCategoryAdmin) :
  activate_perm = 'common.activate_race'

class EthnicityAdmin(BaseCategoryAdmin) :
  activate_perm = 'common.activate_ethnicity'
  
class EthnicOriginAdmin(BaseCategoryAdmin) :
  activate_perm = 'common.activate_ethnic_origin'

class PoliticalUnitTypeAdmin(BaseCategoryAdmin):
  activate_perm = 'common.activate_polunittype'

class LanguageAdmin(BaseCategoryAdmin):
  activate_perm = 'common.activate_language'

admin.site.register(models.PoliticalUnit, PoliticalUnitAdmin)
admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.TemporalLocation, TemporalLocationAdmin)
admin.site.register(models.Religion, ReligionAdmin)
admin.site.register(models.Race, RaceAdmin)
admin.site.register(models.Ethnicity, EthnicityAdmin)
admin.site.register(models.EthnicOrigin, EthnicOriginAdmin)
admin.site.register(models.PoliticalUnitType, PoliticalUnitTypeAdmin)
admin.site.register(models.Language, LanguageAdmin)
