from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('monitor.urls',
    url(r'^/?$', index, name='monitor_index'),
    url(r'log/?$', log , name='monitor_log'),
    url(r'population/?$', population_index , name='monitor_population_index'),
    url(r'population/(?P<pop_id>\d+)/?$', population , name='monitor_population'),
    url(r'student/?$', student_index, name='monitor_student_index'),
    url(r'student/(?P<student_id>\d+)/?$', student, name='monitor_student'))
