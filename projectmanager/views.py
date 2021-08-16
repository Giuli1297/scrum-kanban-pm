from django.shortcuts import render


# Create your views here.


def homepage(request):
    """
    Pagina principal
    :param request:
    :return:
    """

    return render(request, "dashboard/home.html")
