from django.views.generic import View
from projectmanager.models import *
from django.shortcuts import render, redirect
from projectmanager.utils import render_to_pdf
from django.http import HttpResponse
from django.contrib import messages


class VistaReporteView(View):
    """
    Vista para generar los tres diferentes reportes, Product Backlog, Spring Backlog, US - Prioridad
    """

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        context = {
            'proyecto': proyecto
        }
        return render(request, 'reporte/vista_reporte.html', context)


class ViewPdfProductBacklog(View):
    """
    Vista basada en clase utlizada para la generacion del reporte del product backlog
    """

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        product_backlog = proyecto.product_backlog
        context = {
            'productBacklog': product_backlog
        }

        pdf = render_to_pdf("reporte/product_backlog.html", context)
        return pdf


class ViewPdfSpringBacklog(View):
    """
    Vista basada en clase utlizada para la generacion del reporte del sprint backlog
    """

    def get(self, request, slug, pk, *args, **kwargs):
        sprint = Sprint.objects.get(pk=pk)
        context = {
            'sprint': sprint
        }

        pdf = render_to_pdf("reporte/spring_backlog.html", context)
        return pdf


class ViewPdfUSPrioridad(View):
    """
    Vista basada en clase utlizada para la generacion del reporte de la prioridad de UserStory
    """

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint_actual = None
        if hasattr(proyecto, 'sprint_actual'):
            sprint_actual = proyecto.sprint_actual
        else:
            messages.error(request, "No tiene un sprint actual")
            return redirect('proyecto_reporte', slug=proyecto.slug)
        context = {
            'sprint_actual': sprint_actual
        }

        pdf = render_to_pdf("reporte/us_prioridad.html", context)
        return pdf
