from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from firebase_admin import firestore, auth  # Importar auth para autenticación con Firebase Admin
from django.utils.timezone import now  # Para obtener la fecha y hora actual


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
                password=password  # Usar la contraseña proporcionada
            )

            # Crear documento en Firestore para el usuario
            datos_usuario = {
                'email': email,
                'tipo': rol,
                'telefono': telefono,
                'nombre': nombre,
                'uid': user.uid  # Incluir el UID del usuario de Firebase
            }
            crear_documento('usuarios', datos_usuario)

            # Si el rol es 3, verificar o agregar el chofer a la colección choferes
            if rol == 3:  # Rol 3 corresponde a chofer
                # Verificar si ya existe un chofer con este nombre
                choferes_ref = db.collection('choferes')
                query = choferes_ref.where('nombre', '==', nombre).limit(1).get()

                if not query:  # Si no existe un documento con este nombre
                    datos_chofer = {
                        'nombre': nombre,
                        'telefono': telefono,  # Puedes incluir más datos si es necesario
                    }
                    choferes_ref.add(datos_chofer)  # Crear el nuevo documento

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
    id_chofer = request.GET.get('id')  # Obtiene el id de la URL
    return render(request, 'App/chofer_reporte.html', {'id': id_chofer})

def evidencia(request):
    id_chofer = request.GET.get('id')  # Obtiene el id de la URL
    return render(request, 'App/chofer_evidencia.html', {'id': id_chofer})

def chofer_viajes(request):
    id_chofer = request.GET.get('id')  # Obtiene el id de la URL

    # Buscar en la colección 'usuarios' el documento que tenga el campo 'uid' igual a id_chofer
    usuario_documento = obtener_documentos(
        'usuarios', 
        filtros=[('uid', '==', id_chofer)]
    )

    if usuario_documento:
        nombre_chofer = usuario_documento[0].get('nombre')  # Extraer el nombre del chofer del primer documento obtenido

        # Filtrar en la colección 'viajes2' los documentos donde el campo 'chofer' es igual al nombre del chofer
        viajes = obtener_documentos(
            'viajes2', 
            filtros=[('chofer', '==', nombre_chofer)]
        )

        # Diccionario para asignar prioridad a los estados
        estados_prioridad = {'asignado': 1, 'en curso': 2, 'terminado': 3}

        # Ordenar los viajes según el estado
        viajes_ordenados = sorted(
            viajes, 
            key=lambda v: estados_prioridad.get(v.get('estado', ''), 4)
        )
    else:
        viajes_ordenados = []  # Si no se encuentra el usuario, asignar una lista vacía

    # Pasar los viajes ordenados al contexto
    context = {'viajes': viajes_ordenados, 'id': id_chofer}
    return render(request, 'App/chofer_viajes.html', context)
    

@csrf_exempt 
def iniciar_viaje(request):
  if request.method == 'POST':
    try:
      data = json.loads(request.body)
      imagen_url = data.get('imagen_url')

      # Guardar la URL en Firestore
      doc_ref = db.collection('tu_coleccion').document()  # Reemplaza 'tu_coleccion' con el nombre de tu colección
      doc_ref.set({
          'imagen_url': imagen_url,
          # Otros campos que desees guardar
      })

      return JsonResponse({'mensaje': 'URL guardada en Firestore'})
    except Exception as e:
      return JsonResponse({'error': str(e)}, status=500)
  else:
    return JsonResponse({'error': 'Método no permitido'}, status=405)
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
    Los documentos se ordenan por estado: asignado -> en curso -> terminado.
    """
    # Obtener los documentos de la colección 'viajes2'
    viajeprueba = obtener_documentos('viajes2')

    # Diccionario para asignar prioridad a los estados
    estados_prioridad = {'asignado': 1, 'en curso': 2, 'terminado': 3}

    # Ordenar los documentos según el estado
    viajeprueba_ordenado = sorted(
        viajeprueba, 
        key=lambda v: estados_prioridad.get(v.get('estado', ''), 4)
    )

    # Pasar los datos ordenados al contexto
    context2 = {'viajes2': viajeprueba_ordenado}
    return render(request, 'App/monitorista_viajes.html', context2)


def editar_vehiculo(request):
    return render(request, 'App/monitorista_editar_vehiculo.html')

def editar_cliente(request):
    return render(request, 'App/monitorista_editar_cliente.html')

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
