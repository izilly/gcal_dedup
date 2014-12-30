from django.conf.urls import patterns, url
from pick_calendar import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^calendars/(?P<target>\w+)/$', views.calendars, name='calendars'),
    url(r'^calendars/(?P<target>\w+)/selected/$', views.calendars_selected,  
        name='calendars_selected'),
    url(r'^deduplify/$', views.deduplify, name='deduplify'),
    url(r'^reset/$', views.reset, name='reset'),
)

