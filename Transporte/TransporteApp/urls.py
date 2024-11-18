from django.urls import path
from . import views

urlpatterns = [
    path('', views.log_in, name = 'login'),
    path('registro/', views.sign_up, name = "signup"),
    path('bd/', views.bd, name='bd'),


    # ----------------------------------------------------------------- Chofer
    path('menu/chofer', views.menu_chofer, name = 'menuChofer'),
    path('viajes/reporte', views.reportes, name = 'reportes'),
    path('viajes/disponible/evidencia', views.evidencia, name = 'evidencia'),
    path('viajes/disponible', views.chofer_viajes, name = 'viajesDisponibles'),


    # ----------------------------------------------------------------  Monitorista
    path('menu/monitorista', views.menu_monitorista, name = 'menuMonitorista'),
    path('viajes/estados', views.viajes, name = 'viajes'),
    path('viajes/informacion', views.viaje_info, name = 'informacion'),
    path('viajes/asignacion', views.asignar_viaje, name = 'asignacion'),
    path('editar/vehiculos', views.editar_vehiculo, name = 'editarVehiculo'),
    path('editar/clientes', views.editar_cliente, name = 'editarCliente'),


    # ---------------------------------------------------------------- Funciones firestore
    path('crear_viaje/', views.crear_viaje, name='crear_viaje'),
    path('login/', views.log_in, name='login')
]
