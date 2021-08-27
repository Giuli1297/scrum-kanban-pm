from scrum_kanban_pm.settings.common import *

import django_heroku


import environ
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


DEBUG = False

SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: update this when you have the production host
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

SITE_ID = env('SITE_ID')

STATIC_ROOT = os.path.join(BASE_DIR, '../staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '../static')
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

django_heroku.settings(locals())

