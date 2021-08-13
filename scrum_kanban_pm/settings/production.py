from scrum_kanban_pm.settings.common import *
import environ

import environ
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

DEBUG = False

SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: update this when you have the production host
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
