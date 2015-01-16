gcal_dedup
==========



Installation
------------

1. cd into project directory

2. create the settings_secret.py file and modify that file to have a valid 
   SECRET_KEY value

    ```
    cp gcal_dedup/settings_secret.py.template gcal_dedup/settings_secret.py 
    vim gcal_dedup/settings_secret.py 
    ``` 

3. download a client_secret.json file from the Google developers console and 
   save it to `gcal_api/client_secret.json` 

4. create the required databases

    ```
    python2 manage.py syncdb
    ```


