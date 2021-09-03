from scrum_kanban_pm.settings.common import *

# Email configuracion
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'fpunascrumkanban@gmail.com'
EMAIL_HOST_PASSWORD = 'fpunascrumkanban123'