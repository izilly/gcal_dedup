from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from oauth2client.django_orm import Storage
from gcal_api.google_calendar_dups import GCalMover
from auth.models import CredentialsModel

def index(request):
    #TODO: move out of pick_calendar, and into main site
    c = RequestContext(request)
    return render(request, 'pick_calendar/index.html', c)

def calendars(request):
    #TODO: handle when user is not logged in 
    user = request.user 
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    creds = storage.get()
    gcm = GCalMover(creds)
    calendars = gcm.get_calendars()
    context = {'choice_list': calendars,
               'question': 'Select source calendar(s)',
               'error_message': '',
               'form_url': reverse('pick_calendar:select_calendars')}
    return render(request, 'pick_calendar/calendars.html', context)

def select_calendars(request):
    calendar_list = request.POST.getlist('choice')
    return render(request, 
                  'pick_calendar/select_calendars.html', 
                  {'calendar_list': calendar_list})

