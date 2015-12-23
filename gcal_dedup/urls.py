from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import logout
import pick_calendar.views
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('pick_calendar.urls', 
                                    namespace='pick_calendar')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('gcal_auth.urls', 
                                    namespace='gcal_auth')),
)

