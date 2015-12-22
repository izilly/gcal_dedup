from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils.html import escape
import json
from oauth2client.django_orm import Storage
from gcal_api.google_calendar_dups import GCalMover
from gcal_auth.models import CredentialsModel
from django.contrib.auth.decorators import login_required


def index(request):
    #TODO: move out of pick_calendar, and into main site
    #from pudb import set_trace; set_trace()
    progress = get_progress(request)
    context = {'progress': progress,}
    return render(request, 'pick_calendar/index.html', context)

def reset(request):
    progress = get_progress(request, reset=True)
    return redirect('index')

def get_progress(request, reset=False):
    progress = request.session.get('progress')
    if not progress or reset:
        progress = {'source': [],
                    'destination': [],
                    'completed': None,
                    'dryrun': False,
                    'replace_text': False,
                    'select_original': 'created_earliest',
                    'created_earliest': True,
                    'updated_earliest': False,
                    'min_chars': False,
                    'rep1f': '',
                    'rep1r': '',
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
    #return redirect('pick_calendar:index')
    #return redirect('{}#source'.format(reverse('index')))

def deduplify(request):
    #from pudb import set_trace; set_trace()
    progress = get_progress(request)
    source = progress.get('source')
    destination = progress.get('destination')[0]
    user = request.user 
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    creds = storage.get()
    gcm = GCalMover(creds)
    log = gcm.deduplify(source, destination, 
                        html=False,
                        dry_run=progress['dryrun'],
                        )
    #from pudb import set_trace; set_trace()
    progress['log'] = log
    request.session['progress'] = progress
    return redirect('index')

def settings(request):
    #from pudb import set_trace; set_trace()
    progress = get_progress(request)
    dryrun = progress['dryrun']
    select_original = progress['select_original']
    replace_text = progress['replace_text']
    rep1f = escape(progress['rep1f'])
    rep1r = escape(progress['rep1r'])
    context = {'dryrun': dryrun,
               'replace_text': replace_text,
               'select_original': select_original,
               'rep1f': rep1f,
               'rep1r': rep1r,
               'created_earliest': progress['created_earliest'],
               'updated_earliest': progress['updated_earliest'],
               'min_chars': progress['min_chars'],
              }
    context_json = json.dumps(context)
    return render(request, 'pick_calendar/settings.html', {'context': context_json})

def settings_update(request):
    #from pudb import set_trace; set_trace()
    progress = get_progress(request)
    dryrun = request.POST.get('dryrun') is not None
    replace_text = request.POST.get('replace_text') is not None
    select_original = request.POST.get('select_original')
    rep1f = request.POST.get('rep1f')
    rep1r = request.POST.get('rep1r')
    progress['dryrun'] = dryrun
    progress['replace_text'] = replace_text
    progress['select_original'] = select_original
    progress['created_earliest'] = select_original == 'created_earliest'
    progress['updated_earliest'] = select_original == 'updated_earliest'
    progress['min_chars'] = select_original == 'min_chars'
    progress['rep1f'] = rep1f 
    progress['rep1r'] = rep1r
    request.session['progress'] = progress
    return redirect('index')

