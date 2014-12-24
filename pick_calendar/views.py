from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from oauth2client.django_orm import Storage
from gcal_api.google_calendar_dups import GCalMover
from auth.models import CredentialsModel
from django.contrib.auth.decorators import login_required


def index(request):
    #TODO: move out of pick_calendar, and into main site
    c = RequestContext(request)
    return render(request, 'pick_calendar/index.html', c)

def get_progress(request):
    progress = request.session.get('progress')
    if not progress:
        progress = {'source': [],
                    'destination': [],
                    'completed': None,
                    }
        request.session['progress'] = progress
    return progress

@login_required
def calendars(request, target):
    #TODO: handle when user is not logged in 
    user = request.user 
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    creds = storage.get()
    gcm = GCalMover(creds)
    calendars = gcm.get_calendars()
    #from pudb import set_trace; set_trace()
    question = 'Select {} calendar'.format(target)
    if target == 'source':
        form_type = 'checkbox'
        question = '{}(s)'.format(question)
    elif target == 'destination':
        form_type = 'radio'
    context = {'choice_list': calendars,
               'question': question,
               'error_message': '',
               'form_type': form_type,
               'form_url': reverse('pick_calendar:calendars_selected', 
                                   args=(target,))}
    return render(request, 'pick_calendar/calendars.html', context)

def calendars_selected(request, target):
    calendar_list = request.POST.getlist('choice')
    progress = get_progress(request)
    progress[target] = calendar_list
    progress['completed'] = target
    #from pudb import set_trace; set_trace()
    return render(request, 
                  'pick_calendar/calendars_selected.html', 
                  {'calendar_list': calendar_list})

#def select_calendars(request):
    #calendar_list = request.POST.getlist('choice')
    #return render(request, 
                  #'pick_calendar/select_calendars.html', 
                  #{'calendar_list': calendar_list})

