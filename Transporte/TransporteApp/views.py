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

def log_in(request):
    return render(request, 'App/login.html')

def sign_up(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            nombre = request.POST.get('nombre')
            telefono = request.POST.get('telefono')
            rol = int(request.POST.get('rol'))  # Convertir rol a entero

            # Crear usuario en Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password  # Usar la contraseña hasheada
            )

            # Crear documento en Firestore
            datos_usuario = {
                'email': email,
                'tipo': rol, 
                'telefono': telefono,
                'nombre': nombre,
                'uid': user.uid  # Incluir el UID del usuario de Firebase
            }
            crear_documento('usuarios', datos_usuario)

            return JsonResponse({'success': True})

        except Exception as e:  # Capturar cualquier excepción
            error_message = f"Error al crear el usuario: {e}"
            return JsonResponse({'success': False, 'error': error_message})

    return render(request, 'App/signup.html')

# --------------------------------------------------------- Chofer
def menu_chofer(request):
    id_chofer = request.GET.get('id')  # Obtiene el id de la URL
    return render(request, 'App/chofer_menu.html', {'id': id_chofer}) 

def reportes(request):
    return render(request, 'App/chofer_reporte.html')

def evidencia(request):
    return render(request, 'App/chofer_evidencia.html')

def chofer_viajes(request):
    id_chofer = request.GET.get('id')  # Obtiene el id de la URL
    
    # Buscar en la colección 'usuarios' el documento que tenga el campo 'uid' igual a id_chofer
    usuario_documento = obtener_documentos(
        'usuarios', 
        filtros=[('uid', '==', id_chofer)]
    )

    if usuario_documento:
        nombre_chofer = usuario_documento[0].get('nombre')  # Extraer el nombre del chofer del primer documento obtenido

        # Filtrar en la colección 'viajes2' los documentos donde el campo 'nombre' es igual al nombre del chofer
        viajes = obtener_documentos(
            'viajes2', 
            filtros=[('chofer', '==', nombre_chofer)]
        )
    else:
        viajes = []  # Si no se encuentra el usuario, asignar una lista vacía

    context = {'viajes': viajes, 'id': id_chofer}
    return render(request, 'App/chofer_viajes.html', context)

# ------------------------------------------------------------------ Monitorista
def menu_monitorista(request):
    return render(request, 'App/monitorista_menu.html')

def viaje_info(request):
    """
    Vista para obtener y renderizar documentos de la colección 'viajes2' filtrados por nombres.
    """
    dato_estatico = request.GET.get('dato_estatico')
    datos = obtener_documentos('viajes2', filtros=[('chofer', '==', dato_estatico)])
    context3 = {'datos': datos}
    return render(request, 'App/monitorista_info_viaje.html', context3)
 


def asignar_viaje(request):
    choferes = obtener_documentos('choferes')
    vehiculos = obtener_documentos('vehiculos', filtros=[('tipo', '==', 'foraneo')])
    clientes = obtener_documentos('clientes')
    context = {'choferes': choferes, 'vehiculos': vehiculos, 'clientes': clientes}
    return render(request, 'App/monitorista_asignacion.html', context)

def viajes(request):
    """
    Vista para obtener y renderizar documentos de la colección 'viajes2' en la página HTML.
    """
    viajeprueba = obtener_documentos('viajes2')
    context2 = {'viajes2': viajeprueba}
    return render(request, 'App/monitorista_viajes.html', context2)

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
