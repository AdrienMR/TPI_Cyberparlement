from django.shortcuts import render
import requests
from django.views.generic import TemplateView

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


class StartView(TemplateView):
    template_name = 'parlement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parlement'] = get_Parlement()
        return context


class DetailView(TemplateView):
    template_name = 'detail_parlement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['membres'] = membre_parlement(self.kwargs['pk'])
        return context


class ModifMemberView(TemplateView):
    template_name = 'modifi_member.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personne'] = modif_personne(self.kwargs['pk'])
        return context
