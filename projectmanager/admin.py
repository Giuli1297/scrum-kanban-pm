from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Proyecto)

admin.site.register(UserStory)

admin.site.register(Rol)
admin.site.register(Sprint)

admin.site.register(UserInfo)

admin.site.register(HistorialUs)


admin.site.register(UserWorkTime)
admin.site.register(RegistroActividadDiairia)
