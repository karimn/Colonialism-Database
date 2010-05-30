from django.conf.urls.defaults import *

urlpatterns = patterns('colonialismdb.population.views',
    # Example:
    # (r'^colonialismdb/', include('colonialismdb.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^query/download$', 'download_data'),
    (r'^query/', 'query'),
    (r'^$', 'index'),
)

