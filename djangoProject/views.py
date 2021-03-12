from django.http import HttpResponse
import secrets
import string
from django.core.mail import send_mail
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
        if p.cpparent != 1:
            get_parlement_recursif(self, p.cpparent)
            return all_parlement.count()
        else:
            break


def mail_password(request):
    if request.method == 'POST':
        personne = Personne.objects.filter(idpersonne=request.POST.get('id'))
        for p in personne:
            p.password = None
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(8))
            p.password_check = password
            send_mail('code pour reset le passeword',
                      f'Allez sur le lien pour réinitialiser votre password {password}',
                      "rossier.adrien@bluewin.ch",
                      ['adrienmatthieu.rossier@ceff.ch'],
                      fail_silently=False, )
            return password


class Test(DetailView):
    template_name = 'TPI_Cyberparlement/cyberparlement/Password.html'
    model = Personne

    def get_context_data(self, **kwargs):
        context = super(Test, self).get_context_data()
        context['test'] = mail_password(self)
        return context


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
        # context['parlement'] = self.get_parlement(self)
        # context['test'] = reset_password()
        return context


def put_personne(request):
    if request.method == 'POST':
        data = request.POST
        personne = Personne.objects.filter(idpersonne=request.POST.get('id'))
        for p in personne:
            if data['nom']:
                p.nom = data['nom']
            if data['prenom']:
                p.prenom = data['prenom']
            if data['email']:
                p.email = data['email']
            if data['adresse']:
                p.adresse = data['adresse']
            if data['npa']:
                p.npa = data['npa']
            if data['localite']:
                p.localite = data['localite']
            if data['datenaissance']:
                p.datenaissance = data['datenaissance']
            # p.save()
    return HttpResponse('Modifications effectués avec succes')
