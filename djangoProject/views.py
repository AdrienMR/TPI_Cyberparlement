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

# retourne tout les enfants d'un cyberparlement 
# de manière récursive dans une liste
# d'après un id de cyberparlement donné
def get_parlement_recursif(pk, childrens=None):
    if childrens is None:
        childrens = []
    childrens.extend(Cyberparlement.objects.filter(idcyberparlement=pk))
    child = Cyberparlement.objects.filter(cpparent=pk)
    if len(child):
        for c in list(child.values()):
            get_parlement_recursif(c['idcyberparlement'], childrens)
    return childrens

# class qui affiche les données pour 
# la template parlement.html, elle affiche 
# une liste de cyberparlements 
class ParlementListeView(ListView):
    template_name = 'TPI_Cyberparlement/cyberparlement/parlement.html'
    context_object_name = 'parlement'
    model = Cyberparlement

    # met le cyberchancelier choisis
    # sur la page d'avant (home.html)
    # dans la session
    def set_session(self, pk):
        self.request.session['user'] = pk
        return pk

    # retourne l'id du cyberparlement d'ont
    # le cyberchancelier est administrateur
    def get_parlement_chancelier(self, pk):
        membre = Membrecp.objects.only('cyberparlement_id').get(personne=pk, roleCyberparlement=1)
        return membre.cyberparlement_id

    # cette méthode est appelée à chaques fois 
    # qu'une vie basé sur une calss est faite
    # et met les données dans le contexte
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # met dans la session l'id reçu dans la page précédente
        self.set_session(pk=self.kwargs['pk'])
        # met dans le context la liste des parlement et leurs enfants
        context['parlements'] = get_parlement_recursif(self.get_parlement_chancelier(self.request.session['user']))

        return context

# class qui affiche les données: 
# la template parlement_details.html, ces données sont 
# une liste de personnes
class ParlementDetailView(DetailView):
    template_name = 'TPI_Cyberparlement/cyberparlement/parlement_details.html'
    context_object_name = 'membres'
    model = Membrecp

    # retourne une liste de personne ayant 
    # comme cyberparlement de cyberparlement
    # cliqué sur la page d'avent
    def get_personne_membre(self, pk):
        membre = Membrecp.objects.filter(cyberparlement=self.kwargs['pk'])
        all = []
        for m in membre:
            all.append(Personne.objects.filter(idpersonne=m.personne_id))
#         print(self.request.session['user'])
        return all

    # met dans le context la liste des membres d'un cyberparlement
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personnes'] = self.get_personne_membre(self)
        return context

# gènere un code à 8 chiffres et lettres
def gen_code():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    return password

# méthode qui crée et envoie les mails avec les paramètres
# header / text / type
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

# class qui donne les informations pour l'envoie
# de mail pour réinitialiser le mdp
class Password(DetailView):
    template_name = 'TPI_Cyberparlement/personne/Password.html'
    model = Personne

    # met dans le context les infrmationd pour le mail
    def get_context_data(self, **kwargs):
        context = super(Password, self).get_context_data()
        context['mail'] = mail_code(self, 'Code pour reset le password', 'Allez sur le lien pour réinitialiser votre mot de passe', 'password')
#         print(context['mail'])
        return context

# class qui donne les informations pour l'envoie
# de mail util à réinitialisation du mdp
class MailConf(DetailView):
    template_name = 'TPI_Cyberparlement/personne/confirmation_mail.html'
    model = Personne

    # met dans le context les informations- pour le mail
    def get_context_data(self, **kwargs):
        context = super(MailConf, self).get_context_data()
        context['mail'] = mail_code(self, "Code pour confirmer l'adresse mail", 'Allez sur le lien pour confirmer votre adresse mail', 'mail')
#         print(context['mail'])
        return context

# méthode qui génère un pdf pour la confirmation de courrier
# TODO: sujet à améliorations
def courrier_conf(request):
    if request.method == 'POST':
        data = request.POST
        print(data)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, 'Bonjour,')
        p.drawString(100, 705, 'Ceci est une lettre de confirmation de votre adresse postal.')
        p.drawString(100, 690, 'Veuillez mettre le code reçu ci-dessous dans la rebrique')
        p.drawString(100, 675, 'confirmation de courrier qui se trouve dans votre profile')
        p.drawString(100, 660, f" Code: {gen_code()}")
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='Lettre de confirmation postale.pdf')


# class qui affiche les données pour la template
# home.html et affiche la liste de tout les cyberchanceliers
class LoginPage(ListView):
    template_name = 'TPI_Cyberparlement/home.html'
    context_object_name = 'membres'
    model = Membrecp

    # méthode qui retourne la liste des membres qui dont cyberchancelier
    def get_personne_membre(self):
        menbre = Membrecp.objects.filter(roleCyberparlement=1)
        all = []
        for m in menbre:
            all.append(Personne.objects.filter(idpersonne=m.personne_id))
        return all

    # met dans le contect la liste des cyberchanceliers
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personnes'] = self.get_personne_membre()
        return context

# class qui affiche les données pour la template
# modif_membre.html eet ces données sont:
# une personne et une liste de cyberparlement
class ModifMemberView(DetailView):
    template_name = 'TPI_Cyberparlement/personne/modif_membre.html'
    model = Personne

    # méthode qui retourne une personne
    def get_personne_by_id(self, pk):
        return Personne.objects.filter(idpersonne=self.kwargs['pk'])

    # méthode qui retourne une liste de cyberparlement
    def get_parlement(self, pk):
        membre = Membrecp.objects.filter(personne=self.kwargs['pk'])
        for m in membre:
            return Cyberparlement.objects.filter(idcyberparlement=m.cyberparlement.idcyberparlement)

    # met dans le context une personne et un cyberparlement
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personne'] = self.get_personne_by_id(self)
        context['parlement'] = self.get_parlement(self)
        # context['test'] = reset_password()
        return context

# méthode qui modifie une personne
# avec les données reçu dans le post
# et retourne un message si cela à marché
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

# méthode qui supprime un cyberparlement
# d'après les données reçu en post
# et envoie un message si cela à marché
def del_parlement(request):
    if request.method == 'POST':
        data = request.POST
        parlement = Membrecp.objects.filter(cyberparlement=data['idparlement'], personne=data['idpersonne'])
        parlement.delete()
    return HttpResponse(f'Suppression effectués avec succes')

# méthode qui crée des membres d'un cyberparlement
# à partir d'un fichier csv
def csv_import(request):
    if request.method == 'POST':
        data = request.FILES['file']
        personne = Personne.objects
        # vérifie si c'est le bon type de fichier 
        # qui à été choisis
        if not data.name.endswith('.csv'):
            return HttpResponse('THIS IS NOT A CSV FILE')
        else:
            data_set = data.read().decode('utf-8')
            champs = []
            csv_data = csv.reader(io.StringIO(data_set), delimiter=';')
            for row in csv_data:
                champs.append(row)
                # vérifie si les champs nom / prénom / localité
                # ont biens été mis dans le fichier
                if row[0] == '' or row[1] == '' or row[6] == '':
                    return HttpResponse(f'Les champs {champs[0][0]}, {champs[0][1]}, {champs[0][6]} doivent être obligatoirement remplis dans le fichier')
            champs.pop(0)
            # crée une personne pour chaques lignes du csv
            # et crée une instance d'objet pour chaques clef étrangères
            # qui sont dans le model
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
                # crée la relation entre une personne et un cyberparlement
                membre = Membrecp(cyberparlement=parlement, personne=Personne.objects.latest('idpersonne'), roleCyberparlement=rolecp)
                membre.save()
        return HttpResponse(f'Importation faite avec succes {champs}')

# méthode qui assigne une personne à un cyberparlement
def assigner_personne(request):
    return None
