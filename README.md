gcal_dedup
==========

gcal_dedup is a django web app for removing duplicate events from Google 
Calendar.  There is also a stand-alone python script that can be run 
from the command-line, again with the same purpose of deduplifying your 
Google Calendar.  

To prevent any loss of data, duplicate events are never deleted, instead 
they are moved to a separate user-specified calendar.  

NOTE: this software is in the very early stages of developerment but it 
seems to be working fine in my testing so far. 


Installation
------------

1. cd into project directory

2. create the settings_secret.py file and modify that file to have a valid 
   SECRET_KEY value

    ```
    cp gcal_dedup/settings_secret.py.template gcal_dedup/settings_secret.py 
    vim gcal_dedup/settings_secret.py 
    ``` 

3. download a client_secrets.json file from the Google developers console and 
   save it to `gcal_api/client_secrets_web.json` 

4. create the required databases

    ```
    python2 manage.py syncdb
    ```

Command-Line Mode
-----------------

1. clone the repo or just download the gcal_api directory.

2. cd into that directory and run the script.

    ```
    python2 ./gcal_api/google_calendar_dups.py 
    ``` 

3. the script will prompt you to select the source and destination
   calendars.

4. if you have a lot of events in the source calendar(s), it may take a 
   little while to complete.  the script output will print information 
   about the duplicate events that are found/moved.  


