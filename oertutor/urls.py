from django.conf.urls import patterns, include, url
from oertutor.views import *
from oertutor.tutor.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('oertutor.views',
    url(r'^$', tutor, name='main'),
    url(r'^tutor/$', tutor, name='tutor'),
    url(r'^tutor/load$', load, name='tutor_load'),
    url(r'^tutor/forget$', forget, name='tutor_forget'),
    url(r'^tutor/next$', next_step, name='tutor_next'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ga/monitor', include('oertutor.ga.monitor.urls'))
)
