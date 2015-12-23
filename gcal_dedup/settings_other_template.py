#import os.path
#BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
#DATABASES = {}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
#STATIC_URL = '/static/'
#STATIC_ROOT = ''


#TEMPLATE_DEBUG = False

# speed up response time by caching templates
#TEMPLATES = [
    #{
        #'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #'DIRS': [os.path.join(BASE_DIR, 'templates')],
        #'OPTIONS': {
            #'context_processors': [
                #'django.template.context_processors.debug',
                #'django.template.context_processors.request',
                #'django.contrib.auth.context_processors.auth',
                #'django.contrib.messages.context_processors.messages',
            #],
            #'loaders': [
                #('django.template.loaders.cached.Loader', [
                    #'django.template.loaders.filesystem.Loader',
                    #'django.template.loaders.app_directories.Loader',
                    #]
                #),
            #],
        #},
    #}
#]

#ALLOWED_HOSTS = []
