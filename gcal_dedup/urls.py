from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pick_calendar/', include('pick_calendar.urls', 
                                    namespace='pick_calendar')),
)
