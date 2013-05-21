from django.conf.urls import patterns, include, url
from oertutor.views import *
from oertutor.tutor.views import tutor

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('oertutor.views',
    url(r'^$', interface, name='interface'),
    url(r'^nim/$', nim, name='nim'),
    url(r'^tutor/$', tutor, name='tutor'),
    # Examples:
    # url(r'^$', 'oertutor.views.home', name='home'),
    # url(r'^oertutor/', include('oertutor.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
