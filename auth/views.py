from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from oauth2client.client import OAuth2WebServerFlow
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from oauth2client.django_orm import Storage
import json
from auth.models import CredentialsModel


def get_flow(request):
    CLIENT_ID = ('***REMOVED***'
                 '.apps.googleusercontent.com')
    CLIENT_SECRET = '***REMOVED***'
    SCOPE = ('https://www.googleapis.com/auth/calendar ' 
             'https://www.googleapis.com/auth/userinfo.email ' 
             'https://www.googleapis.com/auth/userinfo.profile')
    redirect_uri = request.build_absolute_uri(reverse('auth:authdone'))
    flow = OAuth2WebServerFlow(CLIENT_ID,
                               CLIENT_SECRET,
                               SCOPE,
                               redirect_uri=redirect_uri)
    return flow

def auth(request):
    flow = get_flow(request)
    uri = flow.step1_get_authorize_url()
    return redirect(uri)

def authdone(request):
    flow = get_flow(request)
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
            storage = Storage(CredentialsModel, 'id', user, 'credential')
            storage.put(creds)
        else:
            # TODO: handle 
            pass 
    else:
        # TODO: handle 
        pass 
    return redirect('index')


