from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404

# Create your views here.
from projectmanager.models import Proyecto


@login_required
@permission_required('projectmanager.can_access', raise_exception=True)
def homepage(request):
    """
    Devuelve la pagina principal de la aplicacion

    Parameters
    ----------
    request
        Objeto que contiene info acerca de la solicitud del cliente

    """
    return render(request, "dashboard/home.html")


def homepage2(request):
    return render(request, 'dashboard/home2.html')


def proyecto_detail(request, proyecto_slug):
    """
    Presenta la pagina principla para la gestion de un proyecto
    :param request:
    :return:
    """
    proyecto = get_object_or_404(Proyecto, slug=proyecto_slug)
    return render(request, 'proyecto/detail.html', {'proyecto': proyecto})
