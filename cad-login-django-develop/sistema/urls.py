"""
URL configuration for sistema project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.urls import path
from  cadastro import views as cadastro_view
from  login import views as login_view
from app import views as app_view
from painel import views as painel_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app_view.home, name='home'),
    path('cadastro/', cadastro_view.cadastro, name='cadastro'),
    path('ativar/<uidb64>/<token>/', cadastro_view.ativar_conta, name='ativar_conta'),
    path('login/', login_view.login_view, name='login'),
    path('login/mfa/', login_view.mfa_view, name='mfa'),
    path('painel/', painel_views.painel_principal, name='painel'),
    path('logout/', login_view.logout_view, name='logout'),

    # Rota principal após o login
    path('painel/', login_view.painel_redirect, name='painel_redirect'),
    
    # Rotas específicas de cada nível
    path('painel/administrador/', painel_views.view_administrador, name='view_administrador'),
    path('painel/diretoria/', painel_views.view_diretoria, name='view_diretoria'),
    path('painel/gerencia-geral/', painel_views.view_gerencia_geral, name='view_gerencia_geral'),
    path('painel/gerencia/', painel_views.view_gerencia, name='view_gerencia'),
    path('painel/supervisao/', painel_views.view_supervisao, name='view_supervisao'),
    path('painel/atendente/', painel_views.view_atendente, name='view_atendente'),
    path('painel/caixa/', painel_views.view_caixa, name='view_caixa'),
]
