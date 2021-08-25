from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .utils import account_activation_token

# Create your views here.
from projectmanager.models import Proyecto


@login_required
def homepage(request):
    """
    Devuelve la pagina principal de la aplicacion

    Parameters
    ----------
    request
        Objeto que contiene info acerca de la solicitud del cliente

    """
    return render(request, "dashboard/home.html")



def proyecto_detail(request, proyecto_slug):
    """
    Presenta la pagina principla para la gestion de un proyecto
    :param request:
    :return:
    """
    proyecto = get_object_or_404(Proyecto, slug=proyecto_slug)
    return render(request, 'proyecto/detail.html', {'proyecto': proyecto})


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('home')

            if user.is_active:
                return redirect('home')
            user.is_active = True
            user.save()

            return redirect('home')

        except Exception as ex:
            pass

        return redirect('home')