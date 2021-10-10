from django.contrib.auth.models import Permission
from .proyecto_model import Proyecto
from .rol_model import Rol
from .sprint_model import Sprint
from .user_story_model import UserStory, HistorialUs, UserInfo
from .user_work_model import UserWorkTime
from .system_activity_model import SystemActivity
from .QA_models import QA


def get_name(self):
    return self.name


Permission.add_to_class("__str__", get_name)

__all__ = [
    'Proyecto',
    'Rol',
    'UserInfo',
    'UserWorkTime',
    'Sprint',
    'UserStory',
    'HistorialUs',
    'SystemActivity',
    'QA'
]
