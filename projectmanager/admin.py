from django.contrib import admin

from .models import *

# Register your models here.
from .models.user_story_model import RegistroActividadDiairia, UserStorySprint

admin.site.register(Proyecto)

admin.site.register(UserStory)

admin.site.register(Rol)
admin.site.register(Sprint)

admin.site.register(UserInfo)

admin.site.register(HistorialUs)

admin.site.register(UserWorkTime)
admin.site.register(RegistroActividadDiairia)

admin.site.register(SystemActivity)
admin.site.register(QA)

admin.site.register(CapacidadSMasteSprint)

admin.site.register(UserStorySprint)
