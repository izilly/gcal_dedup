from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import logout
import pick_calendar.views
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', pick_calendar.views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pick_calendar/', include('pick_calendar.urls', 
                                    namespace='pick_calendar')),
    url(r'^accounts/', include('auth.urls', 
                                    namespace='auth')),
)

