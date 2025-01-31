"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('parlement/<int:pk>', views.ParlementListeView.as_view(), name='parlement'),
    path('parlement/detail/<int:pk>', views.ParlementDetailView.as_view(), name='membres_parlement'),
    path('parlement/detail/modif/<int:pk>', views.ModifMemberView.as_view(), name='modif_membre'),
    path('parlement/detail/modif/confirm_changes', views.put_personne, name='confirm_changes'),
    path('parlement/detail/modif/reset_password/<int:pk>', views.Password.as_view(), name='reset_password'),
    path('parlement/detail/mail_conf/<int:pk>', views.MailConf.as_view(), name='mail_conf'),
    path('parlement/detail/courrier_conf', views.courrier_conf, name='courrier_conf'),
    path('parlement/detail/modif/confirm_delete', views.del_parlement, name='confirm_delete'),
    path('parlement/detail/modif/assigner_personne/<int:pk>', views.AssignerPersonne.as_view(), name='assigner_personne'),
    path('parlement/detail/modif/assigner_personne/confirm_add', views.confirm_add, name='confirm_add'),
    path('parlement/import_csv', views.csv_import, name='import_csv'),
]
