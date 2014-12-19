from django.conf.urls import patterns, url
from django.contrib.auth.views import logout


from pick_calendar import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^pick_calendar/', views.pick_calendar, name='pick_calendar'),
    url(r'^picked/', views.picked,  name='picked'),
    url(r'^auth/', views.auth,  name='auth'),
    url(r'^authdone/', views.authdone,  name='authdone'),
    url(r'^logout/', logout, {'template_name': 'pick_calendar/logged_out.html'}, name='logout'),
)

