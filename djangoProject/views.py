from django.http import HttpResponse, response, request, FileResponse, HttpRequest
import secrets
import string
from django.core.mail import send_mail
from django.core import serializers
from django.views.generic import TemplateView, ListView, DetailView
import io
from reportlab.pdfgen import canvas
from djangoProject.models import *


class ParlementListeView(ListView):
    template_name = 'TPI_Cyberparlement/cyberparlement/parlement.html'
    context_object_name = 'parlement'
    model = Cyberparlement
    request = HttpRequest()

    def get_parlementls(self, pk):
        self.request.session['user'] = serializers.serialize('json', pk)
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Koolapic'
        context['description'] = 'La liste des activités sur Koolapic'
        context['parlements'] = self.get_parlementls(self)
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


def test_recursive(pk):
    all = []
    pk = 8
    parlement = Cyberparlement.objects.filter(idcyberparlement=pk)
    for p in parlement:
        if not all.__contains__(p.idcyberparlement):
            all.append(p.idcyberparlement)
        children = Cyberparlement.objects.filter(cpparent=p.idcyberparlement)
        if not children:
            for c in children:
                test_recursive(c.idcyberparlement)
    return True


def gen_code():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password


def mail_code(self, header, text, type):
    personne = Personne.objects.filter(idpersonne=self.kwargs['pk'])
    password = gen_code()
    for p in personne:
        if type == 'password':
            p.password = None
            p.passwordcheck = None
            p.passwordcheck = password
        elif type == 'mail':
            p.mailcheck = password
        send_mail(header,
                  text + ' ' + password,
                  "rossier.adrien@bluewin.ch",
                  ['adrienmatthieu.rossier@ceff.ch'],
                  fail_silently=False, )
        return password


class Password(DetailView):
    template_name = 'TPI_Cyberparlement/personne/Password.html'
    model = Personne

    def get_context_data(self, **kwargs):
        context = super(Password, self).get_context_data()
        context['mail'] = mail_code(self, 'Code pour reset le password', 'Allez sur le lien pour réinitialiser votre mot de passe', 'password')
        print(context['mail'])
        return context


class MailConf(DetailView):
    template_name = 'TPI_Cyberparlement/personne/confirmation_mail.html'
    model = Personne

    def get_context_data(self, **kwargs):
        context = super(MailConf, self).get_context_data()
        context['mail'] = mail_code(self, "Code pour confirmer l'adresse mail", 'Allez sur le lien pour confirmer votre adresse mail', 'mail')
        print(context['mail'])
        return context


def courrier_conf(request):
    if request.method == 'POST':
        data = request.POST
        print(data)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, 'Bonjour,')
        p.drawString(100, 705, 'Ceci est une lettre de confirmation de votre adresse postal.')
        p.drawString(100, 690, 'Veuillez mettre le code reçu ci-dessous dans la rebrique')
        p.drawString(100, 675, 'confirmation de courrier de votre profile')
        p.drawString(100, 660, f"{gen_code()}")
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='Lettre de confirmation postale.pdf')


class LoginPage(ListView):
    template_name = 'TPI_Cyberparlement/home.html'
    context_object_name = 'membres'
    model = Membrecp

    def get_personne_membre(self):
        menbre = Membrecp.objects.filter(roleCyberparlement='CyberChancelier')
        all = []
        for m in menbre:
            all.append(Personne.objects.filter(idpersonne=m.personne_id))
        return all

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personnes'] = self.get_personne_membre()
        return context



class ModifMemberView(DetailView):
    template_name = 'TPI_Cyberparlement/personne/modif_membre.html'
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
            for s in Statutpersonne.objects.filter(idstatut=data['statut']):
                p.statut = s.statut
            # p.save()

    return HttpResponse('Modifications effectués avec succes')
