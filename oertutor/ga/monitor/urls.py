from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('ga.monitor.urls',
    url(r'^/?$', index, name='monitor_index'),
    url(r'population/?$', population_index , name='monitor_population'),
    url(r'population/(?P<pop_id>\d+)/?$', population , name='monitor_population'),
    url(r'student$', student, name='monitor_student'))
