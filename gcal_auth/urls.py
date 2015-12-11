from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout
from gcal_auth import views

urlpatterns = patterns('',
    url(r'^login/$', views.login,  name='login'),
    url(r'^logged_in/', views.logged_in,  name='logged_in'),
    url(r'^logout/', logout, 
        {'template_name': 'gcal_auth/logged_out.html'}, 
        name='logout'),
)
