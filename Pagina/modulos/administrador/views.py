from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from modulos.cliente.models import Usuario, Perfil, Materia, Tema, Contenido, Tarea, EntregaTarea, Cuestionario, Pregunta, Examen, ExamenRevision, ClienteLogeado
from .forms import UsuarioForm, PerfilForm, TemaForm, ContenidoForm, TareaForm, CuestionarioForm, PreguntaForm, MateriaForm
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .utils import procesar_pdf
from django.shortcuts import render
from django.http import JsonResponse
import subprocess
from django.views.decorators.csrf import csrf_exempt
import serial


# Create your views here.

def login_view(request):
    request.session.flush()  # Limpiar la sesión
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Usuario.objects.get(email=email)
            if user.check_password(password):  
                request.session['user_id'] = user.id
                
                # *Registrar el login del usuario*
                ClienteLogeado.objects.create(usuario=user)

                if user.nivel == 1:  
                    return redirect('admin_principal')  
                else:
                    return redirect('cliente_principal') 
            else:
                messages.error(request, 'Correo electrónico o contraseña incorrectos.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Correo electrónico o contraseña incorrectos.')
    
    return render(request, 'administrador/login.html')
def admin_principal(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=user_id)
    materias = usuario.materias.all()
    clientes = ClienteLogeado.objects.select_related('usuario').order_by('-fecha_login')[:5]
    return render(request, 'administrador/principalAdmin.html', {
        'usuario': usuario,
        'materias': materias,
        'clientes': clientes
        
    })

##usuarios
def lista_usuarios(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    if user_id:
        usuarios = Usuario.objects.all()
    return render(request, 'administrador/lista_usuarios.html', {'usuarios': usuarios})
    
def detalle_usuario(request, usuario_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    perfil = usuario.perfil  # Acceder al perfil del usuario

    return render(request, 'administrador/detalle_usuario.html', {
        'usuario': usuario,
        'perfil': perfil
    })
def create_user(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    if request.method == "POST":
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('create_profile', usuario_id=form.instance.id)
    else:
        form = UsuarioForm()
    return render(request, 'administrador/usuario_form.html', {'form': form})
def create_profile(request, usuario_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            return redirect('lista_usuarios')
    else:
        form = PerfilForm()
    return render(request, 'administrador/perfil_form.html', {'form': form, 'usuario': usuario})
def logout_view(request):
    request.session.flush()
    return redirect('login')
def edit_profile(request, usuario_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    perfil = usuario.perfil
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('detalle_usuario', usuario_id=usuario_id)
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'administrador/perfil_form.html', {'form': form, 'usuario': usuario})
def edit_user(request, usuario_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user_data = form.cleaned_data
            if user_data.get('password'):
                usuario.password = make_password(user_data['password'])
            usuario.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('admin_principal')  
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'administrador/usuario_form.html', {'form': form})


##Materias
def detalle_materia(request, materia_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')

    # Obtener la materia
    materia = get_object_or_404(Materia, id=materia_id)
    
    # Obtener los cuestionarios asociados a la materia
    cuestionarios = Cuestionario.objects.filter(materia=materia)
    
    # Obtener los temas relacionados con la materia
    temas = Tema.objects.filter(materia=materia)

    # Prefetch para optimizar las consultas relacionadas con 'contenidos' y 'tareas'
    temas = temas.prefetch_related('contenidos', 'tareas')
    
    # Renderizar el template
    return render(request, 'administrador/detalle_materia.html', {
        'materia': materia,
        'temas': temas,
        'cuestionarios': cuestionarios  # Cambiado a plural para indicar que son varios
    })

#tema
def agregar_materia(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')

    # Obtener el usuario
    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            materia = form.save(commit=False)  # Crear la materia sin guardarla aún
            materia.save()  # Guardar la materia en la base de datos

            # Relacionar la materia con el usuario que la creó
            materia.usuarios.add(usuario)  # Añadir al usuario como parte de la materia
            return redirect('admin_principal')  # Redirigir a la página principal del administrador

    else:
        form = MateriaForm()

    return render(request, 'administrador/crear_materia.html', {'form': form})


def agregar_tema(request, materia_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    materia = get_object_or_404(Materia, id=materia_id)
    
    if request.method == 'POST':
        form = TemaForm(request.POST)
        if form.is_valid():
            nuevo_tema = form.save(commit=False)
            nuevo_tema.materia = materia
            nuevo_tema.save()
            return redirect('detalle_materia_admin', materia_id=materia.id)
    else:
        form = TemaForm()
    
    return render(request, 'administrador/agregar_tema.html', {'form': form, 'materia': materia})
#eliminar tema 
def eliminar_tema(request, tema_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    tema = get_object_or_404(Tema, id=tema_id)
    if request.method == 'POST':
        tema.delete()
        return redirect('detalle_materia_admin', materia_id=tema.materia.id)
    return render(request, 'administrador/confirmar_eliminacionTema.html', {'tema': tema})
#editar tema 
def editar_tema(request, tema_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    tema = get_object_or_404(Tema, id=tema_id)
    if request.method == 'POST':
        form = TemaForm(request.POST, instance=tema)
        if form.is_valid():
            form.save()
            return redirect('detalle_materia_admin', materia_id=tema.materia.id)  # Redirige a la vista de detalle de la materia
    else:
        form = TemaForm(instance=tema)
    return render(request, 'administrador/tema_form.html', {'form': form, 'tema': tema, 'materia': tema.materia})
def agregar_contenido(request, tema_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    tema = get_object_or_404(Tema, id=tema_id)
    if request.method == 'POST':
        form = ContenidoForm(request.POST, request.FILES)
        if form.is_valid():
            contenido = form.save(commit=False)
            contenido.tema = tema
            contenido.save()
            return redirect('detalle_materia_admin', materia_id=tema.materia.id)  # Redirige a la vista de detalle de la materia
    else:
        form = ContenidoForm()
    return render(request, 'administrador/contenido_form.html', {'form': form, 'tema': tema, 'materia': tema.materia})

def editar_contenido(request, contenido_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    contenido = get_object_or_404(Contenido, id=contenido_id)
    if request.method == 'POST':
        form = ContenidoForm(request.POST, request.FILES, instance=contenido)
        if form.is_valid():
            form.save()
            return redirect('detalle_materia_admin', materia_id=contenido.tema.materia.id)  # Redirige a la vista de detalle de la materia
    else:
        form = ContenidoForm(instance=contenido)
    return render(request, 'administrador/contenido_form.html', {'form': form, 'contenido': contenido, 'materia': contenido.tema.materia})
def eliminar_contenido(request, contenido_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    contenido = get_object_or_404(Contenido, id=contenido_id)
    if request.method == 'POST':
        contenido.delete()
        return redirect('detalle_materia_admin', materia_id=contenido.tema.materia.id)
    return render(request, 'administrador/confirmar_eliminacion.html', {'contenido': contenido})
#tarea
def agregar_tarea(request, tema_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    tema = get_object_or_404(Tema, id=tema_id)

    if request.method == 'POST':
        form = TareaForm(request.POST, request.FILES)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.tema = tema
            tarea.save()
            return redirect('detalle_materia_admin', materia_id=tema.materia.id)
    else:
        form = TareaForm()

    return render(request, 'administrador/tarea_form.html', {'form': form, 'tema': tema, 'materia': tema.materia})

def editar_tarea(request, tarea_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            return redirect('detalle_materia_admin', materia_id=tarea.tema.materia.id)  # Redirige a la vista de detalle de la materia
    else:
        form = TareaForm(instance=tarea)
    return render(request, 'administrador/tarea_form.html', {'form': form, 'tarea': tarea, 'materia': tarea.tema.materia})
def eliminar_tarea(request, tarea_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        tarea.delete()
        return redirect('detalle_materia_admin', materia_id=tarea.tema.materia.id)
    return render(request, 'administrador/confirmar_eliminacionT.html', {'tarea': tarea})
#Ver tareas entregas
def lista_usuarios_entregaron_tarea(request, tarea_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    
    tarea = get_object_or_404(Tarea, id=tarea_id)
    entregas = EntregaTarea.objects.filter(tarea=tarea)
    
    return render(request, 'administrador/usuarios_entregaron_tarea.html', {
        'tarea': tarea,
        'entregas': entregas
    })
def lista_usuarios_entregaron_cuestionario(request, cuestionario_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    
    cuestionario = get_object_or_404(Cuestionario, id=cuestionario_id)
    entregas = ExamenRevision.objects.filter(examen__cuestionario=cuestionario)
    
    return render(request, 'administrador/usuarios_entregaron_cuestionario.html', {
        'cuestionario': cuestionario,
        'entregas': entregas
    })
@require_POST
def toggle_revisado(request):
    entrega_id = request.POST.get('entrega_id')  # Obtén el ID enviado por POST
    entrega = get_object_or_404(EntregaTarea, id=entrega_id)  # Busca la entrega

    # Cambiar el estado de revisado al contrario
    entrega.revisado = not entrega.revisado
    entrega.save()

    # Retorna una respuesta JSON indicando el nuevo estado
    return JsonResponse({'success': True, 'revisado': entrega.revisado})
def crear_cuestionario(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)

    # Verificar si el usuario está autenticado
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')

    if request.method == 'POST':
        form = CuestionarioForm(request.POST, request.FILES)
        if form.is_valid():
            cuestionario = form.save(commit=False)
            cuestionario.materia = materia  # Asignar la materia directamente
            cuestionario.save()
            return redirect('detalle_materia_admin', materia_id=materia.id)
    else:
        form = CuestionarioForm()

    return render(request, 'administrador/cuestionario_form.html', {'form': form, 'materia': materia})

#preguntas
def generar_pregunta(request, cuestionario_id):
    # Buscar el cuestionario por el cuestionario_id
    cuestionario = get_object_or_404(Cuestionario, id=cuestionario_id)

    # Obtener el archivo PDF asociado al cuestionario
    pdf_path = cuestionario.archivo.path  # La ruta del archivo PDF

    if pdf_path:
        # Llamar a la función que procesa el PDF y genera las preguntas
        procesar_pdf(pdf_path, cuestionario_id)

        # Redirigir al detalle de la materia después de procesar el PDF
        return redirect('detalle_materia_admin', materia_id=cuestionario.materia.id)
    else:
        # Si no hay PDF asociado al cuestionario, mostrar un mensaje de error
        return render(request, 'administrador/error.html', {
            'mensaje': 'No se ha encontrado un archivo PDF asociado a este cuestionario.'
        })
def detalle_examen_terminado_admin(request, examen_revision_id):
    print('Detalle examen terminado id de revision:', examen_revision_id)
    # Obtener la revisión del examen
    examen_revision = get_object_or_404(ExamenRevision, id=examen_revision_id)

    # Obtener el examen relacionado
    examen = examen_revision.examen

    # Obtener las preguntas asociadas al examen
    preguntas = examen.preguntas.all()

    # Obtener las respuestas del usuario desde el campo respuestas_usuario del modelo ExamenRevision
    respuestas_usuario = examen_revision.respuestas_usuario
    print('Respuestas del usuario desde ExamenRevision:', respuestas_usuario)
    
    # Vincular cada pregunta con su respectiva respuesta del usuario
    preguntas_con_respuestas = []
    for pregunta in preguntas:
        # Buscar la respuesta del usuario para esta pregunta
        respuesta_usuario = next((r for r in respuestas_usuario if str(r['pregunta_id']) == str(pregunta.id)), None)
        respuestas_usuario_texto = respuesta_usuario['respuestas_usuario'] if respuesta_usuario else 'No respondida'

        # Para preguntas OM, dividir las opciones para mostrarlas
        opciones = [opcion.strip() for opcion in pregunta.opciones.split("\n")] if pregunta.tipo == 'OM' else None
        
        # Si es de tipo OM, verificar las opciones seleccionadas
        if pregunta.tipo == 'OM':
            opciones_usuario = [opcion.strip() for opcion in respuestas_usuario_texto.split(',')] if respuestas_usuario_texto != 'No respondida' else []
            opciones_correctas = [opcion.strip() for opcion in pregunta.respuesta.split(',')]
        else:
            opciones_usuario = None
            opciones_correctas = None

        # Agregar la pregunta, la respuesta del usuario y las opciones si es de OM
        preguntas_con_respuestas.append({
            'pregunta': pregunta.pregunta,
            'respuesta_correcta': pregunta.respuesta,
            'respuesta_usuario': respuestas_usuario_texto,
            'opciones': opciones,
            'opciones_usuario': opciones_usuario,
            'opciones_correctas': opciones_correctas
        })
    
    return render(request, 'administrador/detalle_examen_terminado_admin.html', {
        'examen_revision': examen_revision,
        'preguntas_con_respuestas': preguntas_con_respuestas
    })
# views.py

def agregar_pregunta(request, cuestionario_id):
    # Obtener el cuestionario con el ID proporcionado
    cuestionario = get_object_or_404(Cuestionario, id=cuestionario_id)

    # Si el formulario es enviado vía POST
    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        
        if form.is_valid():
            # Guardar la pregunta pero no hacer commit todavía (para asignar el cuestionario)
            pregunta = form.save(commit=False)
            pregunta.cuestionario = cuestionario  # Asignar el cuestionario
            pregunta.save()  # Guardar la pregunta con el cuestionario asignado
            return redirect('detalle_materia_admin', materia_id=cuestionario.materia.id)
    else:
        # Crear un formulario vacío si no es un POST
        form = PreguntaForm()

    # Renderizar el formulario en la plantilla 'agregar_pregunta.html'
    return render(request, 'administrador/agregar_pregunta.html', {
        'form': form,
        'cuestionario': cuestionario  # Pasar el cuestionario al contexto
    })
try:
    arduino = serial.Serial('COM4', 9600)  # Cambia 'COM3' al puerto donde está conectado tu Arduino
except Exception as e:
    arduino = None
    print(f"Error al conectar con Arduino: {e}")


# Vista para controlar el LED en el pin 5
def control_led_view(request):
    return render(request, 'administrador/control_led.html')


# Vista para enviar comandos al LED del pin 5
def control_led(request, led, action):
    if arduino:
        try:
            command = f"{led.upper()}_{action.upper()}\n"
            arduino.write(command.encode())
            return JsonResponse({"status": "success", "command": command})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Arduino no está conectado."})


# Vista para controlar los LEDs de los pines 6, 7 y 8
def control_leds_view(request):
    return render(request, 'administrador/control_leds.html')


# Vista para enviar comandos a los LEDs de los pines 6, 7 y 8
def control_leds(request, led, action):
    if arduino:
        try:
            command = f"{led.upper()}_{action.upper()}\n"
            arduino.write(command.encode())
            return JsonResponse({"status": "success", "command": command})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Arduino no está conectado."})


# Vista para controlar el LED RGB
def control_ledrgb_view(request):
    return render(request, 'administrador/control_ledrgb.html')


# Vista para enviar comandos al LED RGB
def control_ledrgb(request, led, action):
    if arduino:
        try:
            command = f"{led.upper()}_{action.upper()}\n"
            arduino.write(command.encode())
            return JsonResponse({"status": "success", "command": command})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Arduino no está conectado."})


# Vista para la sección Servo
def control_servo_view(request):
    return render(request, 'administrador/control_servo.html')

def control_servo(request, command):
    if arduino:
        try:
            arduino.write(f"{command}\n".encode())  # Enviar comando al Arduino
            return JsonResponse({"status": "success", "command": command})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Arduino no conectado."})

def code_executor_view(request):
    return render(request, 'administrador/execute_code.html')







