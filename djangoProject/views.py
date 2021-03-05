from django.shortcuts import render
import requests
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView

from djangoProject.models import *

BASE_URL = 'http://192.168.20.20:3000/'


def get_Parlement():
    parlement_request = requests.get(f"{BASE_URL}cyberparlement/")
    parlement_data = parlement_request.json()
    return parlement_data


def membre_parlement(pk):
    membre_request = requests.get(f"{BASE_URL}cyberparlement/{pk}/membres")
    membre_data = membre_request.json()
    return membre_data


def modif_personne(pk):
    personne_modif = requests.get(f"{BASE_URL}personne/{pk}")
    personne_data = personne_modif.json()
    return personne_data


class ParlementListeView(ListView):
    template_name = 'TPI_Cyberparlement/cyberparlement/parlement.html'
    context_object_name = 'parlement'
    model = Cyberparlement

    def get_parlementls(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Koolapic'
        context['description'] = 'La liste des activités sur Koolapic'
        context['parlements'] = self.get_parlementls()
        return context


class ParlementDetailView(DetailView):
    template_name = 'TPI_Cyberparlement/cyberparlement/parlement_details.html'
    context_object_name = 'membres'
    model = 'Membrecp'

    def get_membres(self):
        membres = Membrecp.objects.filter(cyberparlement=self.kwargs['pk'])
        return membres

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['membres'] = self.get_membres(self)
        print(self.get_membres(self))
        return context


class ModifMemberView(TemplateView):
    template_name = 'modifi_member.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personne'] = modif_personne(self.kwargs['pk'])
        return context


