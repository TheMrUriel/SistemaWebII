from django.urls import path
from . import views

urlpatterns = [
    path('', views.log_in, name = 'login'),
    path('registro/', views.sign_up, name = "signup"),
    path('home/', views.home, name='home'),
    path('bd/', views.bd, name='bd'),

    # - Chofer
    path('reportes/', views.reportes, name = 'reportes'),
    path('evidencia/', views.evidencia, name = 'evidencia')

    # - Monitorista
]
