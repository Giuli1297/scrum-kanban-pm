from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib import messages

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView
)
from projectmanager.forms import ProyectoForm

from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .utils import account_activation_token 
from django.contrib.auth import get_user_model, authenticate, login, logout

# Create your views here.
from projectmanager.models import Proyecto

@login_required(login_url="/login")
def homepage(request):
    """
    Devuelve la pagina principal de la aplicacion

    Parameters
    ----------
    request
        Objeto que contiene info acerca de la solicitud del cliente

    """
    return render(request, "dashboard/home.html") 

def IniciarSesion(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password) 

        if user is not None:
            login(request, user)
            return redirect("home")

    return render(request, "account/login.html") 

def CerrarSesion(request):
    logout(request)
    return redirect("iniciar_sesion")


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
                messages.error(request, "El usuario no pudo ser habilitado2")
                return redirect('home')

            if user.is_active:
                messages.error(request, "El usuario no pudo ser habilitado1")
                return redirect('home')
            user.is_active = True
            user.save()

            messages.success(request, "Usuario " + user.username + " habilitado")
            return redirect('home')
        except Exception as ex:
            messages.error(request, "El usuario no pudo ser habilitado")
            return redirect('home')



class ProyectoCreate(CreateView):
    """
	Vista basada en clase el sirve para crear un proyecto nuevo
	"""
    model = Proyecto
    form_class = ProyectoForm
    template_name = "proyecto/proyecto_form.html"
    success_url = reverse_lazy('proyecto_listar')

class ProyectoView(ListView):
	"""
	Vista basada en clase el cual lista todos los proyectos
	"""
	model = Proyecto
	template_name = 'proyecto/proyecto_list.html'

class ProyectoUpdate(UpdateView):
	"""
	Vista basada en clase el sirve para crear un proyecto nuevo
	"""
	model = Proyecto #Indicar el modelo a utilizar
	form_class = ProyectoForm #Indicar el formulario
	template_name = 'proyecto/proyecto_form.html' #Indicar el template
	success_url = reverse_lazy('proyecto_listar') #Redireccionar 

def registro(request):
    if request.method == "POST":
        name = request.POST.get("nombre")
        last_name = request.POST.get("apellido")
        email = request.POST.get("email")
        password = request.POST.get("password") 
        User = get_user_model()
        user = User.objects.create_user(email, name, last_name, password)
        print(user)
        return redirect('iniciar_sesion')
    return render(request, "account/registro.html")
