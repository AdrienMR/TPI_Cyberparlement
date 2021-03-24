import csv
from datetime import datetime

from django.http import HttpResponse, FileResponse
import secrets
import string
from django.core.mail import send_mail
from django.views.generic import ListView, DetailView
import io
from reportlab.pdfgen import canvas
from djangoProject.models import *

# retourne l'id du parlement d'ont
# l'id donné est cyberchancelier
def get_parlement_chancelier(pk):
    membre = Membrecp.objects.only('cyberparlement').get(personne=pk, roleCyberparlement=1)
    return membre.cyberparlement_id

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
        print(self.request.session['user'])
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
    def get_membres(self, pk):
        personnes = []
        membres = get_parlement_recursif(pk)
        for m in membres:
            mb = Membrecp.objects.filter(cyberparlement=m.idcyberparlement).values('personne_id')
            for b in mb:
                personnes.extend(Personne.objects.filter(idpersonne=b['personne_id']))
        return personnes

    # met dans le context la liste des membres d'un cyberparlement
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personnes'] = self.get_membres(self.kwargs['pk'])
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


# class qui donne les informations pour l'envoie
# de mail pour réinitialiser le mdp
class Password(DetailView):
    template_name = 'TPI_Cyberparlement/personne/confirmation_mail.html'
    model = Personne

    # met dans le context les infrmationd pour le mail
    def get_context_data(self, **kwargs):
        context = super(Password, self).get_context_data()
        context['mail'] = mail_code(self, 'Code pour reset le password', 'Veuillez réinitialiser votre mot de passe, un mot de passe temporaire vous à été assigner \nvoici votre code:', 'password')
        return context


# class qui donne les informations pour l'envoie
# de mail util à réinitialisation du mdp
class MailConf(DetailView):
    template_name = 'TPI_Cyberparlement/personne/confirmation_mail.html'
    model = Personne

    # met dans le context les informations- pour le mail
    def get_context_data(self, **kwargs):
        context = super(MailConf, self).get_context_data()
        context['mail'] = mail_code(self, "Code pour confirmer l'adresse mail", 'Veuillez entrer le code reçu dans la rebrique \'confirmation d\'email\' \nqui se trouve dans votre profile \nvoici votre code:', 'mail')
        return context


# méthode qui génère un pdf pour la confirmation de courrie
# TODO: sujet à améliorations
def courrier_conf(request):
    if request.method == 'POST':
        data = request.POST
        # print(data)
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
class HomePage(ListView):
    template_name = 'TPI_Cyberparlement/cyberparlement/home.html'
    context_object_name = 'membres'
    model = Membrecp

    # méthode qui retourne la liste des membres qui dont cyberchancelier
    def get_personne_membre(self):
        membre = Membrecp.objects.filter(roleCyberparlement=1)
        all = []
        for m in membre:
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
        all = []
        membre = Membrecp.objects.filter(personne=self.kwargs['pk'])
        for m in membre:
            all.extend(Cyberparlement.objects.filter(idcyberparlement=m.cyberparlement.idcyberparlement))
        return all

    # met dans le context une personne et un cyberparlement
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personne'] = self.get_personne_by_id(self)
        # print(self.get_personne_by_id(self).values())
        context['parlement'] = self.get_parlement(self)
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
            p.save()
    return HttpResponse('<h1 class=\"center\">Modifications effectués avec succes</h1>')


# méthode qui supprime un cyberparlement
# d'après les données reçu en post
# et envoie un message si cela à marché
def del_parlement(request):
    if request.method == 'POST':
        data = request.POST
        parlement = Membrecp.objects.filter(cyberparlement=data['idparlement'], personne=data['idpersonne'])
        parlement.delete()
    return HttpResponse(f'<h1>Suppression effectués avec succes</h1>')


# méthode qui crée des membres d'un cyberparlement
# à partir d'un fichier csv
def csv_import(request):
    if request.method == 'POST':
        data = request.FILES['file']
        # vérifie si c'est le bon type de fichier 
        # qui à été choisis
        personne = Personne.objects
        if not data.name.endswith('.csv'):
            return HttpResponse('<h1>Veuillez choisir un fichier avec l\'extension  .csv</h1>')
        else:
            data_set = data.read().decode('utf-8')
            champs = []
            csv_data = csv.reader(io.StringIO(data_set), delimiter=';')
            for row in csv_data:
                champs.append(row)
                # vérifie si les champs nom / prénom / localité
                # ont biens été mis dans le fichier
                if row[0] == '' or row[1] == '' or row[6] == '':
                    return HttpResponse(f'<h1>Les champs {champs[0][0]}, {champs[0][1]}, {champs[0][6]} doivent être obligatoirement remplis dans le fichier</h1>')
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
        return HttpResponse(f'<h1>Importation faite avec succes des perssonnes </h1> <br> {champs}')


# méthode qui assigne une personne à un cyberparlement
class AssignerPersonne(DetailView):
    template_name = 'TPI_Cyberparlement/personne/parlement_add.html'
    model = Personne

    # retourne tout les parlement d'ont
    # l'utilisateur est membre
    def assigned_parlement(self):
        return Membrecp.objects.only('cyberparlement').filter(personne=self.kwargs['pk'])

    # fait le tei avec tout les cyberparlements
    # et retourne que ceux auquel il n'est pas assigné
    def tri(self):
        parlement = get_parlement_recursif(get_parlement_chancelier(self.request.session['user']))
        for i in parlement:
            for a in self.assigned_parlement():
                if i.idcyberparlement == a.cyberparlement.idcyberparlement:
                    parlement.remove(i)
        if parlement:
            return parlement

    # met dans le context une personne et une liste de cyberparlement
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parlement'] = self.tri()
        context['personne'] = self.kwargs['pk']
        return context

# ajoute un utilisateur en tant que membre d'un cyberparlement
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
