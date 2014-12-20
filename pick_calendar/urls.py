from django.conf.urls import patterns, url
from pick_calendar import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^calendars/', views.calendars, name='calendars'),
    url(r'^select_calendars/', views.select_calendars,  
        name='select_calendars'),
)

