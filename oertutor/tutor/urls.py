from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('tutor.urls',
    url(r'^/?$', tutor, name='tutor'),
    url(r'^/mt/?$', aws_mt, name='mt'),
    url(r'^/load/?$', load, name='tutor_load'),
    url(r'^/forget/?$', forget, name='tutor_forget'),
    url(r'^/next/?$', next_step, name='tutor_next')
)
