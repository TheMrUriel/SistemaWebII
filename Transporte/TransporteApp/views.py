from django.shortcuts import render
from django.http import HttpResponse
from firebase_admin import firestore

def home(request):
    return render(request, 'App/Inicio.html')

def log_in(request):
    return render(request, 'App/login.html')

def sign_up(request):
    return render(request, 'App/signup.html')

# - Chofer
def reportes(request):
    return render(request, 'App/chofer_reporte.html')

def evidencia(request):
    return render(request, 'App/chofer_evidencia.html')

def bd(request):
    db = firestore.client()
    viajes_ref = db.collection('viajes')  # Referencia a la colección "viajes"

    # Obtener el último documento de "viajes" ordenado por fecha (o el campo que uses)
    last_doc = viajes_ref.order_by('fecha', direction=firestore.Query.DESCENDING).limit(1).get()

    if last_doc:
        ultimo_viaje = last_doc[0].to_dict()  # Convertir el documento a un diccionario
    else:
        ultimo_viaje = None  # Si no hay documentos, asigna None

    context = {'ultimo_viaje': ultimo_viaje}
    return render(request, 'App/bd.html', context)