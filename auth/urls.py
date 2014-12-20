from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout
from auth import views

urlpatterns = patterns('',
    url(r'^auth/', views.auth,  name='auth'),
    url(r'^authdone/', views.authdone,  name='authdone'),
    url(r'^logout/', logout, 
        {'template_name': 'auth/logged_out.html'}, 
        name='logout'),
)
