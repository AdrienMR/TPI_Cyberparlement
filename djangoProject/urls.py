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
    path('admin/', admin.site.urls),
    path('parlement/', views.ParlementListeView.as_view(), name='parlement'),
    path('parlement/detail/<int:pk>', views.ParlementDetailView.as_view(), name='membres_parlement'),
    path('parlement/detail/modif/<int:pk>', views.ModifMemberView.as_view(), name='modif_membre'),
    path('parlement/detail/modif/confirm_changes', views.put_personne, name='confirm_changes'),
    path('parlement/detail/modif/reset_password/<int:pk>', views.Test.as_view(), name='reset_password'),
]
