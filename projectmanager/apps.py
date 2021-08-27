from django.apps import AppConfig


class ProjectmanagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projectmanager'
    verbose_name = ('projectmanager')

    def ready(self):
        import projectmanager.signals