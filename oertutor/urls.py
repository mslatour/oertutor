from django.conf.urls import patterns, include, url
from oertutor.tutor.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('oertutor.views',
    url(r'^$', include('oertutor.tutor.urls')),
    url(r'^tutor', include('oertutor.tutor.urls')),
    url(r'^monitor', include('oertutor.monitor.urls')),
    url(r'^admin/', include(admin.site.urls))
)
