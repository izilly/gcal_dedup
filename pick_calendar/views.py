from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from gcal_api.google_calendar_dups import GCalMover
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
import json

from django.contrib.auth.models import User
from oauth2client.django_orm import Storage
from pick_calendar.models import CredentialsModel
from django.contrib.auth import authenticate, login


def index(request):
    #from pudb import set_trace; set_trace()
    gcm = GCalMover()
    calendars = gcm.get_calendars()
    #calendar_list = None #TODO: get calendar_list
    context = {'choice_list': calendars,
               'question': 'Select source calendar(s)',
               'error_message': '',
               'form_url': reverse('pick_calendar:pick_calendar')}
    return render(request, 'pick_calendar/index.html', context)

def pick_calendar(request):
    #from pudb import set_trace; set_trace()
    calendar_list = request.POST.getlist('choice')
    return picked(request, calendar_list=calendar_list)

def picked(request, calendar_list=None):
    return render(request, 
                  'pick_calendar/picked.html', 
                  {'calendar_list': calendar_list})

def authdone(request):
    from pudb import set_trace; set_trace()
    CLIENT_ID = '***REMOVED***.apps.googleusercontent.com'
    CLIENT_SECRET = '***REMOVED***'
    SCOPE = ('https://www.googleapis.com/auth/calendar ' 
          'https://www.googleapis.com/auth/userinfo.email ' 
          'https://www.googleapis.com/auth/userinfo.profile')
    redirect_uri = 'http://localhost:8000/pick_calendar/authdone/'
    flow = OAuth2WebServerFlow(CLIENT_ID,
                               CLIENT_SECRET,
                               SCOPE,
                               redirect_uri=redirect_uri)
    code = request.GET['code']
    creds = flow.step2_exchange(code)
    creds_json = json.loads(creds.to_json())
    try:
        email = creds_json.get('id_token').get('email')
    except:
        email = None
    if email:
        try:
            user = User.objects.get(username=email)
        except:
            user = User(username=email)
            user.set_password(email)
            user.save()
        user = authenticate(username=email, password=email)
        if user is not None:
            login(request, user)
        else:
            # TODO: handle 
            pass 
    else:
        # TODO: handle 
        pass 

    gcm = GCalMover(creds)
    calendars = gcm.get_calendars()
    #calendar_list = None #TODO: get calendar_list
    context = {'choice_list': calendars,
               'question': 'Select source calendar(s)',
               'error_message': '',
               'form_url': reverse('pick_calendar:pick_calendar')}
    return render(request, 'pick_calendar/index.html', context)


def auth(request):
    CLIENT_ID = '***REMOVED***.apps.googleusercontent.com'
    CLIENT_SECRET = '***REMOVED***'
    SCOPE = ('https://www.googleapis.com/auth/calendar ' 
          'https://www.googleapis.com/auth/userinfo.email ' 
          'https://www.googleapis.com/auth/userinfo.profile')
    redirect_uri = 'http://localhost:8000/pick_calendar/authdone/'
    flow = OAuth2WebServerFlow(CLIENT_ID,
                               CLIENT_SECRET,
                               SCOPE,
                               redirect_uri=redirect_uri)
    #request.session['flow'] = flow
    uri = flow.step1_get_authorize_url()
    return redirect(uri)
