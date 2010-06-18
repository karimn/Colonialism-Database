from colonialismdb.common import models

from django.contrib import admin

class BaseSubmitAdmin(admin.ModelAdmin) :
  def activate(self, request, query_set):
    """ 
    We should have a concurrency problem here if more than one person are trying to activate entries at the same time.  
    We could use "SELECT FOR UPDATE ..." or the django-locking module, but I would rather wait for 
    http://code.djangoproject.com/ticket/2705 to be integrated into Django.
    """
    rows_activated = 0

    for entry in query_set:
      if entry.active == False:
        entry.active = True
        entry.save()
        entry.log.approved_by = request.user
        entry.log.save()
        rows_activated =+ 1

    if rows_activated > 0:
      self.message_user(request, '%i %s activated' % (rows_activated, 'entry' if rows_activated == 1 else 'entries'))

  activate.short_description = 'Activate'

  actions = ['activate',]

class LocationAdmin(BaseSubmitAdmin) :
  pass

admin.site.register(models.Location, LocationAdmin)
