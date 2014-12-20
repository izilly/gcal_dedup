from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import logout
import views
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pick_calendar/', include('pick_calendar.urls', 
                                    namespace='pick_calendar')),
    url(r'^auth/', views.auth,  name='auth'),
    url(r'^authdone/', views.authdone,  name='authdone'),
    url(r'^logout/', logout, 
        {'template_name': 'logged_out.html'}, 
        name='logout'),
)
