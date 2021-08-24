from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.core.mail import send_mail
from scrum_kanban_pm.settings.development import EMAIL_HOST_USER
from django.contrib.auth.models import User


@receiver(user_signed_up)
def send_email_to_admin(request, user, **kwargs):
    admin = User.objects.get(groups__name='Administrador')
    user.is_active = False
    send_mail(
        '<Subject>User {} has been created'.format(user.username),
        '<Body>A new user has been created',
        EMAIL_HOST_USER,
        [admin.email],
        fail_silently=False,
    )
    print('SUccess?')
