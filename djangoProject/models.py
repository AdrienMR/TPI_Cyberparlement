from django.db import models


class Personnes(models.Model):
    Nom = models.CharField(max_length=45)
    Prenom = models.CharField(max_length=45)
    Genre = models.CharField(max_length=45)
    Email = models.CharField(max_length=45)
    Adresse = models.CharField(max_length=45)
    NPA = models.CharField(max_length=45)
    Localite = models.CharField(max_length=45)
    Status = models.CharField(max_length=45)
    DateDeNaissance = models.CharField(max_length=45)
    NoTel = models.CharField(max_length=45)
    Password = models.CharField(max_length=45)


class CyberParlement(models.Model):
    Nom = models.CharField(max_length=45)
    Description = models.CharField(max_length=45)
    Visibilite = models.CharField(max_length=45)
    Statut = models.CharField(max_length=45)
    idParent = models.IntegerField(45)


class Membre(models.Model):
    personnes = models.ForeignKey(Personnes, null=True, on_delete=models.CASCADE, verbose_name="Personne")
    cyberParlement = models.ForeignKey(CyberParlement, null=True, on_delete=models.CASCADE, verbose_name="CyberParlement")
    RoleCP = models.CharField(max_length=45)