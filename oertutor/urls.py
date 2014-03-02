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
    # Examples:
    # url(r'^$', 'oertutor.views.home', name='home'),
    # url(r'^oertutor/', include('oertutor.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
