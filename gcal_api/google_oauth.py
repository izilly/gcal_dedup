#!/usr/bin/env python2

import httplib2
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run


class GoogleAuthService(object):

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

        # The scope URL for read/write access to a user's calendar data
        self.scope = 'https://www.googleapis.com/auth/calendar'

        # Create a flow object. This object holds the client_id, client_secret, and
        # scope. It assists with OAuth 2.0 steps to get user authorization and
        # credentials.
        self.flow = OAuth2WebServerFlow(self.client_id, self.client_secret, self.scope)

        #def main():

        # Create a Storage object. This object holds the credentials that your
        # application needs to authorize access to the user's data. The name of the
        # credentials file is provided. If the file does not exist, it is
        # created. This object can only hold credentials for a single user, so
        # as-written, this script can only handle a single user.
        self.storage = Storage('credentials.dat')

        # The get() function returns the credentials for the Storage object. If no
        # credentials were found, None is returned.
        self.credentials = self.storage.get()

        # If no credentials are found or the credentials are invalid due to
        # expiration, new credentials need to be obtained from the authorization
        # server. The oauth2client.tools.run() function attempts to open an
        # authorization server page in your default web browser. The server
        # asks the user to grant your application access to the user's data.
        # If the user grants access, the run() function returns new credentials.
        # The new credentials are also stored in the supplied Storage object,
        # which updates the credentials.dat file.
        if self.credentials is None or self.credentials.invalid:
            self.credentials = run(self.flow, self.storage)

        # Create an httplib2.Http object to handle our HTTP requests, and authorize it
        # using the credentials.authorize() function.
        self.http = httplib2.Http()
        self.http = self.credentials.authorize(self.http)

        # The apiclient.discovery.build() function returns an instance of an API service
        # object can be used to make API calls. The object is constructed with
        # methods specific to the calendar API. The arguments provided are:
        #   name of the API ('calendar')
        #   version of the API you are using ('v3')
        #   authorized httplib2.Http() object that can be used for API calls
        self.service = build('calendar', 'v3', http=self.http)



#except AccessTokenRefreshError:
    ## The AccessTokenRefreshError exception is raised if the credentials
    ## have been revoked by the user or they have expired.
    #print ('The credentials have been revoked or expired, please re-run'
        #'the application to re-authorize')

