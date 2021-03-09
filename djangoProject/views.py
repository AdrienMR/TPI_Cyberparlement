from django.http import HttpResponse
from django.shortcuts import render
import requests
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView

from djangoProject.models import *


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
        context['parlements'] = self.get_parlementls()
        return context


class ParlementDetailView(DetailView):
    template_name = 'TPI_Cyberparlement/cyberparlement/parlement_details.html'
    context_object_name = 'membres'
    model = Membrecp

    def get_personne_membre(self, pk):
        membre = Membrecp.objects.filter(cyberparlement=self.kwargs['pk'])
        test = []
        for m in membre:
            test.append(Personne.objects.filter(idpersonne=m.personne_id))
        return test

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personnes'] = self.get_personne_membre(self)
        return context


def get_parlement_recursif(self, pk):
    all_parlement = []
    parlement = Cyberparlement.objects.filter(idcyberparlement=self.kwargs['pk'])
    for p in parlement:
        print(p.cpparent)
        all_parlement.append(p.cpparent)
        if p.cpparent is not 1:
            get_parlement_recursif(self, p.cpparent)
            return all_parlement.count()
        else:
            break



class ModifMemberView(DetailView):
    template_name = 'TPI_Cyberparlement/cyberparlement/modif_membre.html'
    model = Personne

    def get_perdonne_by_id(self, pk):
        return Personne.objects.filter(idpersonne=self.kwargs['pk'])

    def get_parlement(self, pk):
        membre = Membrecp.objects.filter(personne=self.kwargs['pk'])
        for m in membre:
            print(get_parlement_recursif(self, m.cyberparlement))
            return print()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personne'] = self.get_perdonne_by_id(self)
        context['parlement'] = self.get_parlement(self)
        return context


def put_personne(request):
    if request.method == 'POST':
        data = request.POST
        personne = Personne.objects.filter(idpersonne=request.POST.get('id'))
        for p in personne:
            p.nom = data['nom']
            p.prenom = data['prenom']
            p.email = data['email']
            p.adresse = data['adresse']
            p.npa = data['npa']
            p.localite = data['localite']
            p.datenaissance = data['datenaissance']
            # p.save()
    return HttpResponse('Modifications effectués avec succes')
