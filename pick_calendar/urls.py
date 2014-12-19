from django.conf.urls import patterns, url
from django.contrib.auth.views import logout


from pick_calendar import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^calendars/', views.calendars, name='calendars'),
    url(r'^select_calendars/', views.select_calendars,  
        name='select_calendars'),
    url(r'^auth/', views.auth,  name='auth'),
    url(r'^authdone/', views.authdone,  name='authdone'),
    url(r'^logout/', logout, 
        {'template_name': 'pick_calendar/logged_out.html'}, 
        name='logout'),
)

