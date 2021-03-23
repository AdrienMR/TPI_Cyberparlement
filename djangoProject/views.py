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


def get_parlement_chancelier(pk):
    if not pk:
        membre = Membrecp.objects.only('cyberparlement_id').get(personne=pk, roleCyberparlement=1)
        return membre.cyberparlement_id


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.set_session(pk=self.kwargs['pk'])
        context['title'] = 'Koolapic'
        context['description'] = 'La liste des activités sur Koolapic'
        context['parlements'] = get_parlement_recursif(get_parlement_chancelier(self.request.session['user']))

        return context


class ParlementDetailView(DetailView):
    template_name = 'TPI_Cyberparlement/cyberparlement/parlement_details.html'
    context_object_name = 'membres'
    model = Membrecp

    def get_membres(self, pk):
        personnes = []
        membres = get_parlement_recursif(pk)
        for m in membres:
            mb = Membrecp.objects.filter(cyberparlement=m.idcyberparlement).values('personne_id')
            for b in mb:
                personnes.extend(Personne.objects.filter(idpersonne=b['personne_id']))
        return personnes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personnes'] = self.get_membres(self.kwargs['pk'])
        return context


def gen_code():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password


def mail_code(self, header, text, type):
    personne = Personne.objects.filter(idpersonne=self.kwargs['pk'])
    admin = Personne.objects.only('email').get(idpersonne=self.request.session['user'])
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
                  "noreply.cyberparlement@ceff.ch",
                  [p.email, admin.email],
                  fail_silently=False, )
        return password


class Password(DetailView):
    template_name = 'TPI_Cyberparlement/personne/confirmation_mail.html'
    model = Personne

    def get_context_data(self, **kwargs):
        context = super(Password, self).get_context_data()
        context['mail'] = mail_code(self, 'Mot de passe temporaire', 'Ceci est un mot de passe temporaire, veuillez le changer au plus vite. Code:', 'password')
        print(context['mail'])
        return context


class MailConf(DetailView):
    template_name = 'TPI_Cyberparlement/personne/confirmation_mail.html'
    model = Personne

    def get_context_data(self, **kwargs):
        context = super(MailConf, self).get_context_data()
        context['mail'] = mail_code(self, "Code pour confirmer l'adresse mail", 'Allez sur le le site et entrez ce code confirmer votre adresse mail', 'mail')
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

    def get_personne_by_id(self, pk):
        return Personne.objects.filter(idpersonne=self.kwargs['pk'])

    def get_parlement(self, pk):
        all = []
        membre = Membrecp.objects.filter(personne=self.kwargs['pk'])
        for m in membre:
            all.extend(Cyberparlement.objects.filter(idcyberparlement=m.cyberparlement.idcyberparlement))
        print(all)
        return all

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personne'] = self.get_personne_by_id(self)
        context['parlement'] = self.get_parlement(self)
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
                p.genre = Genrepersonne.objects.only('idgenre').get(idgenre=s.idgenre)
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
                p.statut = Statutpersonne.objects.only('idstatut').get(idstatut=s.idstatut)
            # p.save()
    return HttpResponse('<h1 class=\"center\">Modifications effectués avec succes</h1>')


def del_parlement(request):
    if request.method == 'POST':
        data = request.POST
        parlement = Membrecp.objects.filter(cyberparlement=data['idparlement'], personne=data['idpersonne'])
        parlement.delete()
    return HttpResponse(f'<h1>Suppression effectués avec succes</h1>')


def csv_import(request):
    if request.method == 'POST':
        data = request.FILES['file']
        # personne = Personne.objects
        if not data.name.endswith('.csv'):
            return HttpResponse('<h1>Veuillez choisir un fichier avec l\'extension  .csv</h1>')
        else:
            data_set = data.read().decode('utf-8')
            champs = []
            csv_data = csv.reader(io.StringIO(data_set), delimiter=';')
            for row in csv_data:
                champs.append(row)
                if row[0] == '' or row[1] == '' or row[6] == '':
                    return HttpResponse(f'<h1>Les champs {champs[0][0]}, {champs[0][1]}, {champs[0][6]} doivent être obligatoirement remplis dans le fichier</h1>')
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
                # personne.save()
                membre = Membrecp(cyberparlement=parlement, personne=Personne.objects.latest('idpersonne'), roleCyberparlement=rolecp)
                # membre.save()
        return HttpResponse(f'<h1>Importation faite avec succes des perssonnes </h1> <br> {champs}')


class AssignerPersonne(DetailView):
    template_name = 'TPI_Cyberparlement/personne/parlement_add.html'
    model = Personne

    def assigned_parlement(self):
        return Membrecp.objects.only('cyberparlement').filter(personne=self.kwargs['pk'])

    def test(self):
        print(get_parlement_chancelier(self.request.session['user']))
        parlement = get_parlement_recursif(get_parlement_chancelier(self.request.session['user']))
        for i in parlement:
            for a in self.assigned_parlement():
                if i.idcyberparlement == a.cyberparlement.idcyberparlement:
                    parlement.remove(i)
        return parlement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parlement'] = self.test()
        context['personne'] = self.kwargs['pk']
        return context


def confirm_add(request):
    parlement = Cyberparlement.objects.only('idcyberparlement').get(idcyberparlement=request.POST['parlement'])
    rolecp = Rolemembrecp.objects.only('nom').get(nom='membre')
    personne = Personne.objects.only('idpersonne').get(idpersonne=request.POST['personne'])
    membre = Membrecp(
        personne=personne,
        cyberparlement=parlement,
        roleCyberparlement=rolecp
    )
    membre.save()
    return HttpResponse('<h1>Personne Assigné avec succes</h1>')
