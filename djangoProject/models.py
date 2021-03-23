# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser


class Candidat(models.Model):
    idcandidat = models.AutoField(db_column='idCandidat', primary_key=True)  # Field name made lowercase.
    idelection = models.ForeignKey('Election', models.DO_NOTHING, db_column='idElection')  # Field name made lowercase.
    idpersonne = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idPersonne')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'candidat'
        unique_together = (('idelection', 'idpersonne'),)


class Choixinitiative(models.Model):
    idchoixinitiative = models.AutoField(db_column='idChoixInitiative', primary_key=True)  # Field name made lowercase.
    idinitiative = models.ForeignKey('Initiative', models.DO_NOTHING, db_column='idInitiative')  # Field name made lowercase.
    choix = models.CharField(db_column='Choix', max_length=45, blank=True, null=True)  # Field name made lowercase.
    ordre = models.IntegerField(db_column='Ordre', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'choixinitiative'


class Cyberparlement(models.Model):
    idcyberparlement = models.AutoField(db_column='idCyberParlement', primary_key=True)  # Field name made lowercase.
    nom = models.CharField(db_column='Nom', max_length=45)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=200, blank=True, null=True)  # Field name made lowercase.
    visibilite = models.CharField(db_column='Visibilite', max_length=45, blank=True, null=True)  # Field name made lowercase.
    statut = models.ForeignKey('Statutensemble', models.DO_NOTHING, db_column='Statut', blank=True, null=True)  # Field name made lowercase.
    cpparent = models.ForeignKey('self', models.DO_NOTHING, db_column='CPParent', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'cyberparlement'


class Election(models.Model):
    idelection = models.AutoField(db_column='idElection', primary_key=True)  # Field name made lowercase.
    echeance = models.DateTimeField(db_column='Echeance', blank=True, null=True)  # Field name made lowercase.
    sujet = models.CharField(db_column='Sujet', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'election'


class Forum(models.Model):
    idforum = models.OneToOneField(Cyberparlement, models.DO_NOTHING, db_column='idForum', primary_key=True)  # Field name made lowercase.
    idensemble = models.IntegerField(db_column='idEnsemble', blank=True, null=True)  # Field name made lowercase.
    nom = models.CharField(db_column='Nom', max_length=45, blank=True, null=True)  # Field name made lowercase.
    statut = models.CharField(db_column='Statut', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'forum'


class Genrepersonne(models.Model):
    idgenre = models.AutoField(db_column='idGenrepersonne', primary_key=True, )  # Field name made lowercase.
    type = models.CharField(db_column='Type', blank=True, null=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'genrepersonne'


class Statutpersonne(models.Model):
    idstatut = models.AutoField(db_column='idStatutpersonne', primary_key=True)  # Field name made lowercase.
    statut = models.CharField(db_column='Statut', blank=True, null=True, max_length=45)

    class Meta:
        managed = True
        db_table = 'statutpersonne'


class Initiative(models.Model):
    idinitiative = models.AutoField(db_column='idInitiative', primary_key=True)  # Field name made lowercase.
    idcp = models.ForeignKey(Cyberparlement, models.DO_NOTHING, db_column='idCP')  # Field name made lowercase.
    nom = models.CharField(db_column='Nom', max_length=45, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=1000)  # Field name made lowercase.
    echeance = models.DateTimeField(db_column='Echeance')  # Field name made lowercase.
    idinitiateur = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idInitiateur', blank=True, null=True)  # Field name made lowercase.
    statut = models.ForeignKey('Statutinitiative', models.DO_NOTHING, db_column='Statut', blank=True, null=True)  # Field name made lowercase.
    modevalidation = models.ForeignKey('Modevalidation', models.DO_NOTHING, db_column='ModeValidation', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'initiative'


class Rolemembrecp(models.Model):
    rolecp = models.AutoField(db_column='RoleCP', primary_key=True)  # Field name made lowercase.
    nom = models.CharField(db_column='Nom', max_length=45, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'rolemembrecp'


class Membrecp(models.Model):
    idmembrecp = models.AutoField(db_column='idMembreCP', primary_key=True)  # Field name made lowercase.
    personne = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idPersonne')  # Field name made lowercase.
    cyberparlement = models.ForeignKey(Cyberparlement, models.DO_NOTHING, db_column='idCyberParlement')  # Field name made lowercase.
    roleCyberparlement = models.ForeignKey('Rolemembrecp', models.DO_NOTHING, db_column='RoleCP')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'membrecp'
        unique_together = (('idmembrecp', 'personne'),)


class Message(models.Model):
    idmessage = models.AutoField(db_column='idMessage', primary_key=True)  # Field name made lowercase.
    forum = models.ForeignKey(Forum, models.DO_NOTHING, db_column='idForum', blank=True, null=True)  # Field name made lowercase.
    auteur = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idAuteur', blank=True, null=True)  # Field name made lowercase.
    contenu = models.CharField(db_column='Contenu', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'message'


class Modevalidation(models.Model):
    modevaltexte = models.CharField(db_column='ModeValTexte', primary_key=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'modevalidation'


class Personne(models.Model):
    idpersonne = models.AutoField(db_column='idPersonne', primary_key=True)  # Field name made lowercase.
    nom = models.CharField(db_column='Nom', max_length=45)  # Field name made lowercase.
    prenom = models.CharField(db_column='Prenom', max_length=45)  # Field name made lowercase.
    genre = models.ForeignKey(Genrepersonne, models.DO_NOTHING, db_column="genre", blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=45, blank=True, null=True)  # Field name made lowercase.
    adresse = models.CharField(db_column='Adresse', max_length=45, blank=True, null=True)  # Field name made lowercase.
    npa = models.IntegerField(db_column='NPA', blank=True, null=True)  # Field name made lowercase.
    localite = models.CharField(db_column='Localite', max_length=45)  # Field name made lowercase.
    statut = models.ForeignKey(Statutpersonne, models.DO_NOTHING, db_column="statut", blank=True, null=True)  # Field name made lowercase.
    datenaissance = models.DateField(db_column='DateNaissance', blank=True, null=True)  # Field name made lowercase.
    notel = models.CharField(db_column='NoTel', max_length=45, blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=45, blank=True, null=True)  # Field name made lowercase.
    passwordcheck = models.CharField(db_column='PasswordCheck', max_length=45, blank=True, null=True)  # Field name made lowercase.
    mailcheck = models.CharField(db_column='MailCheck', max_length=45, blank=True, null=True)  # Field name made lowercase.
    addresscheck = models.CharField(db_column='AddresseCheck', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'personne'


class Statutensemble(models.Model):
    statuttexte = models.CharField(db_column='StatutTexte', primary_key=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'statutensemble'


class Statutinitiative(models.Model):
    statuttexte = models.CharField(db_column='StatutTexte', primary_key=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'statutinitiative'


class Voteelection(models.Model):
    idelection = models.OneToOneField(Election, models.DO_NOTHING, db_column='idElection', primary_key=True)  # Field name made lowercase.
    personne = models.ForeignKey(Personne, models.DO_NOTHING, db_column='idPersonne')  # Field name made lowercase.
    candidat = models.ForeignKey(Candidat, models.DO_NOTHING, db_column='idCandidat', blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'voteelection'
        unique_together = (('idelection', 'personne'),)


class Voteinitiative(models.Model):
    idvoteinitiative = models.AutoField(db_column='idVoteInitiative', primary_key=True)  # Field name made lowercase.
    personne = models.ForeignKey(Personne, models.DO_NOTHING, db_column='idPersonne')  # Field name made lowercase.
    choixinitiative = models.ForeignKey(Choixinitiative, models.DO_NOTHING, db_column='idChoixInitiative', blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp')  # Field name made lowercase.
    initiative = models.ForeignKey(Initiative, models.DO_NOTHING, db_column='idInitiative')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'voteinitiative'
        unique_together = (('personne', 'initiative'),)
