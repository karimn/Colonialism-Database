from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin, databrowse
admin.autodiscover()

from django.contrib.auth.decorators import login_required

from common.models import Location, Religion, Ethnicity, Race, EthnicOrigin
from population.models import MainDataEntry
from common.models import *

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
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^$','common.views.index'),
    (r'^economics$','economics.views.econsearch'),
    (r'^education$','education.views.edusearch'),
    (r'^government$','government.views.govtsearch'),
    (r'^population$','population.views.popsearch'),    

    #(r'^population/', include('colonialismdb.population.urls')),

    (r'^admin/merge_selected/', 'colonialismdb.common.admin.merge_selected'),
    (r'^admin/(?P<from_applabel>[^/]+)/(?P<from_model>[^/]+)/((add)|(\d+))/autocomplete/(?P<to_applabel>[^/]+)/(?P<to_model>[^/]+)/$', 'colonialismdb.common.views.autocomplete'),
    (r'^admin/(?P<from_applabel>[^/]+)/(?P<from_model>[^/]+)/(?P<from_id>\d+)/get_label/(?P<to_applabel>[^/]+)/(?P<to_model>[^/]+)/$', 'colonialismdb.common.views.get_label'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^static/sources/(?P<path>.+)\.(?P<ext>.+)', 'colonialismdb.sources.views.open_src_file'),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^databrowse/(.*)', login_required(databrowse.site.root)),
)

if settings.DEBUG:
  urlpatterns += patterns('',
      (r'^static/(?P<path>sources/.+)$', 'django.views.static.serve', { 'document_root' : settings.MEDIA_ROOT }),  
  )
