from django.urls import path
from . import views

urlpatterns = [
    path('', views.log_in, name = 'login'),
    path('registro/', views.sign_up, name = "signup"),
    path('bd/', views.bd, name='bd'),


    # ----------------------------------------------------------------- Chofer
    path('menuChofer/', views.menu_chofer, name = 'menuChofer'),
    path('reportes/', views.reportes, name = 'reportes'),
    path('evidencia/', views.evidencia, name = 'evidencia'),
    path('viajesDisponibles/', views.chofer_viajes, name = 'viajesDisponibles'),


    # ----------------------------------------------------------------  Monitorista
    path('menuMonitorista/', views.menu_monitorista, name = 'menuMonitorista'),
    path('viajes/', views.viajes, name = 'viajes'),
    path('informacion/', views.viaje_info, name = 'informacion'),
    path('asignacion/', views.asignar_viaje, name = 'asignacion'),


    # ---------------------------------------------------------------- Funciones firestore
    path('crear_viaje/', views.crear_viaje, name='crear_viaje'),
    path('login/', views.log_in, name='login')
]
