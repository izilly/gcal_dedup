from django.conf.urls import patterns, url
from django.contrib.auth.views import logout


from pick_calendar import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^select_calendar/', views.select_calendar, name='select_calendar'),
    url(r'^select_calendar_result/', views.select_calendar_result,  
        name='select_calendar_result'),
    url(r'^auth/', views.auth,  name='auth'),
    url(r'^authdone/', views.authdone,  name='authdone'),
    url(r'^logout/', logout, 
        {'template_name': 'pick_calendar/logged_out.html'}, 
        name='logout'),
)

