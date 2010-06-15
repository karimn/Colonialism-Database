from django.conf.urls.defaults import *

from django.contrib import admin, databrowse
admin.autodiscover()

from django.contrib.auth.decorators import login_required

from common.models import Location, Religion, Ethnicity, Race, EthnicOrigin
from population.models import MainDataEntry

databrowse.site.register(Location)
databrowse.site.register(Religion)
databrowse.site.register(Ethnicity)
databrowse.site.register(Race)
databrowse.site.register(EthnicOrigin)
databrowse.site.register(MainDataEntry)

urlpatterns = patterns('',
    # Example:
    # (r'^colonialismdb/', include('colonialismdb.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^population/', include('colonialismdb.population.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^databrowse/(.*)', login_required(databrowse.site.root)),
)

