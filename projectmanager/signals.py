from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from scrum_kanban_pm.settings.development import EMAIL_HOST_USER

from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import  urlsafe_base64_encode
from .utils import account_activation_token
from django.urls import reverse


@receiver(user_signed_up)
def send_email_to_admin(request, user, **kwargs):
    admin = User.objects.get(groups__name='Administrador')
    user.is_active = False
    current_site = get_current_site(request)
    email_body = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    }

    link = reverse('activate', kwargs={
        'uidb64': email_body['uid'], 'token': email_body['token']})

    email_subject = 'Usuario nuevo registrado'

    activate_url = 'http://' + current_site.domain + link

    email = EmailMessage(
        email_subject,
        'El usuario ' + user.username + 'se ha registrado, \n Activar Cuenta: \n' + activate_url,
        EMAIL_HOST_USER,
        [admin.email],
    )
    email.send(fail_silently=False)
