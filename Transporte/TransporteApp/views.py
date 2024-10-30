from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from firebase_admin import firestore, auth  # Importar auth para autenticación con Firebase Admin

# Inicializar Firestore
db = firestore.client()

# ------------------------ Funciones para Firestore --------------------------- #
def crear_documento(coleccion, datos):
    """Crea un nuevo documento en la colección especificada."""
    db.collection(coleccion).add(datos)

def obtener_documento(coleccion, id_documento):
    """Obtiene un documento específico de la colección."""
    doc_ref = db.collection(coleccion).document(id_documento)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None

def obtener_documentos(coleccion, orden=None, limite=None, filtros=None):
    """
    Obtiene documentos de la colección, con opciones de ordenamiento, límite y filtros.
    """
    docs_ref = db.collection(coleccion)
    if orden:
        docs_ref = docs_ref.order_by(orden)
    if limite:
        docs_ref = docs_ref.limit(limite)
    if filtros:
        for filtro in filtros:
            campo, operador, valor = filtro
            docs_ref = docs_ref.where(campo, operador, valor)
    docs = docs_ref.stream()
    return [doc.to_dict() for doc in docs]

def actualizar_documento(coleccion, id_documento, datos):
    """Actualiza un documento existente en la colección."""
    doc_ref = db.collection(coleccion).document(id_documento)
    doc_ref.update(datos)

def borrar_documento(coleccion, id_documento):
    """Borra un documento de la colección."""
    db.collection(coleccion).document(id_documento).delete()

# ----------------------------------- Vistas ----------------------------------#

def crear_viaje(request):
    if request.method == 'POST':
        try:
            # Obtener los datos del viaje enviados por AJAX
            chofer = request.POST.get('chofer')
            destino = request.POST.get('destino')
            caja = request.POST.get('caja')
            unidad = request.POST.get('camion')
            origen = request.POST.get('origen')
            sello = request.POST.get('sello')
            cliente = request.POST.get('cliente')
            cporte = request.POST.get('cporte')

            # Crear un diccionario con los datos del viaje
            datos_viaje = {
                'camion': unidad,
                'caja': caja,
                'chofer': chofer,
                'origen': origen,
                'destino': destino,
                'sello': sello,
                'cliente': cliente,
                'cporte': cporte,
                'estado': "asignado"
            }

            # Llamar a la función para crear el documento en Firestore
            crear_documento('viajes2', datos_viaje)

            # Devolver una respuesta exitosa
            return JsonResponse({'mensaje': 'Viaje creado exitosamente'})
        except Exception as e:
            # Devolver una respuesta de error
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def home(request):
    return render(request, 'App/monitorista_viajes.html')

def log_in(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('username')
            password = request.POST.get('password')

            # Autenticar usuario con Firebase Admin
            user = auth.get_user_by_email(email)
            # Firebase Admin no permite autenticación directa con contraseña.
            # Necesitarías implementar autenticación personalizada.

            # Esto es solo para verificar si el usuario existe y obtener su UID
            request.session['user_id'] = user.uid

            # Redirige al usuario a la página principal
            return redirect('home')

        except auth.AuthError as e:
            error_message = f"Error de autenticación: {e}"
            return render(request, 'App/login.html', {'error': error_message})

    return render(request, 'App/login.html')

def sign_up(request):
    return render(request, 'App/signup.html')

# --------------------------------------------------------- Chofer
def reportes(request):
    return render(request, 'App/chofer_reporte.html')

def evidencia(request):
    return render(request, 'App/chofer_evidencia.html')

def chofer_viajes(request):
    return render(request, 'App/chofer_viajes.html')

# ------------------------------------------------------------------ Monitorista
def viaje_info(request):
    return render(request, 'App/monitorista_info_viaje.html')

def asignar_viaje(request):
    choferes = obtener_documentos('choferes')
    vehiculos = obtener_documentos('vehiculos', filtros=[('tipo', '==', 'foraneo')])
    clientes = obtener_documentos('clientes')
    context = {'choferes': choferes, 'vehiculos': vehiculos, 'clientes': clientes}
    return render(request, 'App/monitorista_asignacion.html', context)

def viajes(request):
    return render(request, 'App/monitorista_viajes.html')

# ------------------------------------------------------------------- Archivo de prueba de Base de datos
def bd(request):
    viajes_ref = db.collection('viajes')  # Referencia a la colección "viajes"

    # Obtener el último documento de "viajes" ordenado por fecha
    last_doc = viajes_ref.order_by('fecha', direction=firestore.Query.DESCENDING).limit(1).get()

    if last_doc:
        ultimo_viaje = last_doc[0].to_dict()  # Convertir el documento a un diccionario
    else:
        ultimo_viaje = None  # Si no hay documentos, asigna None

    context = {'ultimo_viaje': ultimo_viaje}
    return render(request, 'App/bd.html', context)
