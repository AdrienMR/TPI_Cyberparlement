import csv
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse, FileResponse, HttpRequest
import secrets
import string
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.generic import ListView, DetailView
import io
from reportlab.pdfgen import canvas
from djangoProject.models import *


def get_parlement_recursif(pk, childrens=None):
    if childrens is None:
        childrens = []
    childrens.extend(Cyberparlement.objects.filter(idcyberparlement=pk))
    child = Cyberparlement.objects.filter(cpparent=pk)
    if len(child):
        for c in list(child.values()):
            get_parlement_recursif(c['idcyberparlement'], childrens)
    return childrens


class ParlementListeView(ListView):
    template_name = 'TPI_Cyberparlement/cyberparlement/parlement.html'
    context_object_name = 'parlement'
    model = Cyberparlement

    def set_session(self, pk):
        self.request.session['user'] = pk
        return pk

    def get_parlement_chancelier(self, pk):
        membre = Membrecp.objects.only('cyberparlement_id').get(personne=pk, roleCyberparlement=1)
        return membre.cyberparlement_id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.set_session(pk=self.kwargs['pk'])
        context['title'] = 'Koolapic'
        context['description'] = 'La liste des activités sur Koolapic'
        context['parlements'] = get_parlement_recursif(self.get_parlement_chancelier(self.request.session['user']))

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
        print(self.request.session['user'])
        return test

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personnes'] = self.get_personne_membre(self)
        return context


def gen_code():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password


def mail_code(self, header, text, type):
    personne = Personne.objects.filter(idpersonne=self.kwargs['pk'])
    password = gen_code()
    for p in personne:
        if type == 'password':
            p.password = password
            p.passwordcheck = None
            p.passwordcheck = password
        elif type == 'mail':
            p.mailcheck = password
        send_mail(header,
                  text + ' ' + password,
                  "rossier.adrien@bluewin.ch",
                  ['adrienmatthieu.rossier@ceff.ch', 'rossier.adrien@bluewin.ch'],
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
        menbre = Membrecp.objects.filter(roleCyberparlement=1)
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
            return Cyberparlement.objects.filter(idcyberparlement=m.cyberparlement.idcyberparlement)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personne'] = self.get_perdonne_by_id(self)
        context['parlement'] = self.get_parlement(self)
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
            for s in Genrepersonne.objects.filter(idgenre=data['genre']):
                p.genre = s.genre
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
            p.save()
    return HttpResponse('Modifications effectués avec succes')


def del_parlement(request):
    if request.method == 'POST':
        data = request.POST
        parlement = Membrecp.objects.filter(cyberparlement=data['idparlement'], personne=data['idpersonne'])
        parlement.delete()
    return HttpResponse(f'Suppression effectués avec succes')


def csv_import(request):
    if request.method == 'POST':
        data = request.FILES['file']
        personne = Personne.objects
        if not data.name.endswith('.csv'):
            return HttpResponse('THIS IS NOT A CSV FILE')
        else:
            data_set = data.read().decode('utf-8')
            champs = []
            csv_data = csv.reader(io.StringIO(data_set), delimiter=';')
            for row in csv_data:
                champs.append(row)
                if row[0] == '' or row[1] == '' or row[6] == '':
                    return HttpResponse(f'Les champs {champs[0][0]}, {champs[0][1]}, {champs[0][6]} doivent être obligatoirement remplis dans le fichier')
            champs.pop(0)
            for row in champs:
                genre = Genrepersonne.objects.only('type').get(type=row[2])
                statut = Statutpersonne.objects.only('statut').get(statut='Confirmé courrier')
                parlement = Cyberparlement.objects.only('idcyberparlement').get(idcyberparlement=request.POST['parlement'])
                rolecp = Rolemembrecp.objects.only('nom').get(nom='membre')
                personne = Personne(
                    nom=row[0],
                    prenom=row[1],
                    genre=genre,
                    email=row[3],
                    adresse=row[4],
                    npa=int(row[5]),
                    localite=row[6],
                    datenaissance=datetime.strptime(row[7], '%Y-%m-%d') if row[7] != '' else None,
                    statut=statut
                )
                personne.save()
                membre = Membrecp(cyberparlement=parlement, personne=Personne.objects.latest('idpersonne'), roleCyberparlement=rolecp)
                membre.save()
        return HttpResponse(f'Importation faite avec succes {champs}')


def assigner_personne(request):
    return None