from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from oauth2client.django_orm import Storage
from gcal_api.google_calendar_dups import GCalMover
from auth.models import CredentialsModel
from django.contrib.auth.decorators import login_required


def index(request):
    #TODO: move out of pick_calendar, and into main site
    #from pudb import set_trace; set_trace()
    progress = get_progress(request)
    context = {'progress': progress,}
    return render(request, 'pick_calendar/index.html', context)

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
    #DONE: handle when user is not logged in 
    user = request.user 
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    creds = storage.get()
    gcm = GCalMover(creds)
    calendars = gcm.get_calendars()
    progress = get_progress(request)
    progress['calendar_list'] = calendars
    request.session['progress'] = progress
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

def get_selected(request, progress):
    calendar_idxs = request.POST.getlist('choice')
    calendar_idxs = [int(i) for i in calendar_idxs]
    calendar_list = progress.get('calendar_list')
    calendars_selected = [calendar_list[i] for i in calendar_idxs]
    return calendars_selected

def calendars_selected(request, target):
    #from pudb import set_trace; set_trace()
    progress = get_progress(request)
    calendars_selected = get_selected(request, progress)
    progress[target] = calendars_selected
    progress['completed'] = target
    request.session['progress'] = progress
    return redirect('index')
    #return render(request, 
                  #'pick_calendar/calendars_selected.html', 
                  #{'calendar_list': calendars_selected})


#----------------------------------------------------------------------------

#DONE: redirect back to index after choosing source/dest calendars 
#        (rather than 'success' results page

#DONE: disable destination calendar selection when source calendars not selected

#TODO: remove source calendar(s) from list of destination calendar choices

#DONE: add a link to reset, start over in source/destination sections 

#TODO: add color to selected calendars 

#TODO: add info/instructions to top of index page 

#TODO: add info about creating a new destination calendar (coming-soon) 

#TODO: add a start/reset button to top of index page 

#----------------------------------------------------------------------------

