from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Usuario, Perfil, Materia, EntregaTarea, Tarea, Cuestionario, Pregunta, Examen, ExamenRevision, ClienteLogeado
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import random
from .forms import PerfilForm, UsuarioForm, EntregaTareaForm
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.http import JsonResponse
import subprocess
from django.views.decorators.csrf import csrf_exempt
import serial
from .forms import RegistroMateriaForm

# Create your views here.
def cliente_principal(request):
    # Obtener el usuario desde la sesión
    user_id = request.session.get('user_id')
    if user_id:
        usuario = Usuario.objects.get(id=user_id)
        # Obtener las materias asociadas al usuario
        materias = usuario.materias.all()
        clientes = ClienteLogeado.objects.select_related('usuario').order_by('-fecha_login')[:5]
    else:

        usuario = None
        materias = []

    return render(request, 'cliente/principal.html', {'usuario': usuario, 'materias': materias, 'clientes': clientes})
def detalle_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    perfil = get_object_or_404(Perfil, usuario=usuario)
    return render(request, 'cliente/detalle_usuario.html', {'usuario': usuario, 'perfil': perfil})
def edit_profile(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    perfil = get_object_or_404(Perfil, usuario=usuario)
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('cliente_principal')
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'cliente/edit_profile.html', {'form': form})
def edit_user(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            # Obtener los datos del formulario
            user_data = form.cleaned_data

            # Si la contraseña no está vacía, encriptarla
            if user_data.get('password'):
                usuario.password = make_password(user_data['password'])
            
            # Guardar el usuario con la contraseña encriptada
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('cliente_principal')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'cliente/edit_user.html', {'form': form})
def registro_materia(request):
    if request.method == 'POST':
        form = RegistroMateriaForm(request.POST)
        if form.is_valid():
            sigla_materia = form.cleaned_data['sigla_materia']
            try:
                # Buscar la materia por la sigla
                materia = Materia.objects.get(sigla=sigla_materia)
                # Registrar al estudiante en la materia
                user_id = request.session.get('user_id')
                usuario = Usuario.objects.get(id=user_id)
                usuario.materias.add(materia)  # Asumiendo que tienes una relación many-to-many
                messages.success(request, 'Te has registrado exitosamente en la materia.')
                return redirect('cliente_principal')  # Redirige al inicio
            except Materia.DoesNotExist:
                messages.error(request, 'No se encontró ninguna materia con esa sigla.')
                return redirect('registro_materia')  # Redirige al formulario en caso de error
    else:
        form = RegistroMateriaForm()

    return render(request, 'cliente/registro_materia.html', {'form': form})
def detalle_materia(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    temas = materia.temas.all()

    # Obtener el user_id de la sesión
    user_id = request.session.get('user_id')
    entregas_por_tarea = {}
    examenes_usuario = []
    examenes_por_cuestionario = {}
    cuestionarios_con_resultado = []

    # Limpiar las sesiones después de guardar
    if 'preguntas_seleccionadas' in request.session:
        del request.session['preguntas_seleccionadas']
    if 'respuesta_usuario_revicion' in request.session:
        del request.session['respuesta_usuario_revicion']
    
    if user_id:
        usuario = get_object_or_404(Usuario, id=user_id)
        
        # Obtener todas las entregas del usuario
        entregas = EntregaTarea.objects.filter(usuario=usuario, tarea__tema__materia=materia)
        
        # Obtener todos los exámenes de revisión del usuario relacionados con los cuestionarios de la materia
        examenes_usuario = ExamenRevision.objects.filter(usuario=usuario, examen__cuestionario__materia=materia)
        
        # Crear un diccionario para marcar las tareas entregadas
        for entrega in entregas:
            entregas_por_tarea[entrega.tarea.id] = True
        print('entregas_por_tarea:', entregas_por_tarea)

        # Crear un diccionario para contar exámenes por cuestionario
        for examen_revision in examenes_usuario:
            cuestionario_id = examen_revision.examen.cuestionario.id
            if cuestionario_id in examenes_por_cuestionario:
                examenes_por_cuestionario[cuestionario_id] += 1
            else:
                examenes_por_cuestionario[cuestionario_id] = 1

        # Crear una lista de True/False dependiendo de si existen 2 o más exámenes de revisión
        resultado_examenes = {}
        for cuestionario_id, count in examenes_por_cuestionario.items():
            if count >= 2:
                resultado_examenes[cuestionario_id] = True
            else:
                resultado_examenes[cuestionario_id] = False

        # Imprimir la lista con True/False
        print('resultado_examenes:', resultado_examenes)
        for cuestionario in materia.cuestionarios.all():
            count_examenes = ExamenRevision.objects.filter(usuario=usuario, examen__cuestionario=cuestionario).count()
            if count_examenes >= 2:
                cuestionarios_con_resultado.append({
                    'cuestionario': cuestionario,
                    'ya_realizado': True
                })
            else:
                cuestionarios_con_resultado.append({
                    'cuestionario': cuestionario,
                    'ya_realizado': False
                })

        print('cuestionarios_con_resultado:', cuestionarios_con_resultado)

    return render(request, 'cliente/detalle_materia.html', {
        'materia': materia,
        'temas': temas,
        'entregas_por_tarea': entregas_por_tarea,
        'examenes_usuario': examenes_usuario,
        'resultado_examenes': resultado_examenes,  # Pasar la lista al template
        'cuestionarios_con_resultado': cuestionarios_con_resultado
        
    })  
#Agregar tarea
def agregar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    materia = tarea.tema.materia  # Accedemos a la materia a través de la tarea

    if request.method == 'POST':
        form = EntregaTareaForm(request.POST, request.FILES)
        if form.is_valid():
            entrega = form.save(commit=False)
            entrega.tarea = tarea
            # Usar el user_id de la sesión o un usuario específico
            user_id = request.session.get('user_id')
            usuario = get_object_or_404(Usuario, id=user_id)
            entrega.usuario = usuario
            entrega.save()
            return redirect('detalle_materia_alumno', materia_id=materia.id)  # Redirigir a la página de detalle de la materia
    else:
        form = EntregaTareaForm()

    return render(request, 'cliente/subir_tarea.html', {'form': form, 'tarea': tarea, 'materia': materia})

#examen
def tomar_examen(request, cuestionario_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('login')
    notar = 0
    cuestionario = get_object_or_404(Cuestionario, id=cuestionario_id)

    if request.method == 'GET':
        preguntas = list(cuestionario.preguntas.all())
        preguntas_seleccionadas = random.sample(preguntas, min(2, len(preguntas)))

        request.session['preguntas_seleccionadas'] = [pregunta.id for pregunta in preguntas_seleccionadas]
        examenes = Examen.objects.filter(usuario_id=user_id, cuestionario=cuestionario)
        cantidad_examenes = examenes.count()
        print(f"Cantidad de exámenes encontrados para el usuario {user_id} en el cuestionario {cuestionario_id}: {cantidad_examenes}")

        for pregunta in preguntas_seleccionadas:
            if pregunta.tipo == 'OM':  # Opción Múltiple
                pregunta.opciones_divididas = [opcion.strip() for opcion in pregunta.opciones.split("\n")]

        print('Preguntas seleccionadas (ID):')
        for pregunta in preguntas_seleccionadas:
            print(f'Pregunta ID: {pregunta.id}')
            print(f'Pregunta: {pregunta.pregunta}')

        tiempo_limite = timezone.now() + timedelta(minutes=10)
        
        print('Preguntas seleccionadas son:')
        for preguntasnuevas in preguntas_seleccionadas:
            print(f'Pregunta ID de la lista de preguntas: {preguntasnuevas.id}')

        return render(request, 'cliente/examen.html', {
            'preguntas': preguntas_seleccionadas,
            'cuestionario': cuestionario,
            'tiempo_limite': tiempo_limite
        })

    elif request.method == 'POST':
        request.session['respuesta_usuario_revicion'] = []
        preguntas_seleccionadas_ids = request.session.get('preguntas_seleccionadas', [])
        preguntas_seleccionadas = Pregunta.objects.filter(id__in=preguntas_seleccionadas_ids)

        print('Preguntas seleccionadas en la parte del POST:')
        for preguntasnuevaspost in preguntas_seleccionadas:
            print(f'Pregunta ID de la lista de preguntas: {preguntasnuevaspost.id}')
            print(f'Pregunta: {preguntasnuevaspost.pregunta}')

        total_preguntas = len(preguntas_seleccionadas)
        print(f'Total de preguntas: {total_preguntas}')
        print('\n')

        print('Los nombres que recupero el POST:')
        for nombre in request.POST.keys():
            print(nombre)
            print('procesando respuesta 1')
            if nombre.startswith('pregunta_'):
                print('Procesando respuesta 2')
                pregunta_id = nombre.split('_')[1].split('_')[0].strip()
                print(f'ID de la pregunta extraído del POST: {pregunta_id}')
                for preguntasm in preguntas_seleccionadas:
                    print(f'Pregunta ID de la lista de preguntas: {preguntasm.id}')

                pregunta = next((p for p in preguntas_seleccionadas if str(p.id) == pregunta_id), None)
                if pregunta:
                    print('Procesando respuesta 3')
                    print(f'Se encontró la pregunta con ID: {pregunta_id}')
                    print(f'Pregunta tipo: {pregunta.tipo}')
                    if pregunta.tipo == 'RL' or pregunta.tipo == 'FV':
                        if 'respuesta_usuario_revicion' not in request.session:
                            request.session['respuesta_usuario_revicion'] = []
                        respuesta_usuario = request.POST.get(f'pregunta_{pregunta.id}').strip()  # Elimina espacios en blanco de la respuesta
                        request.session['respuesta_usuario_revicion'].append({
                            'pregunta_id': pregunta_id,
                            'respuestas_usuario': respuesta_usuario  # Guardar la respuesta
                        })
                        request.session.modified = True
                        print(f'Respuesta del usuario: {respuesta_usuario}')
                        print(f'Respuesta correcta: {pregunta.respuesta}')
                        print('La pregunta es de tipo RL o FV')
                        if respuesta_usuario == pregunta.respuesta:
                            print('Respuesta correcta')
                            notar += 1
                        else:
                            print('Respuesta incorrecta')
                    elif pregunta.tipo == 'OM':
                        if 'respuesta_usuario_revicion' not in request.session:
                            request.session['respuesta_usuario_revicion'] = []
                        respuestas_usuario = request.POST.getlist(f'pregunta_{pregunta.id}_opciones')
                        # Eliminar espacios en blanco de cada respuesta seleccionada
                        respuestas_usuario_limpias = [respuesta.strip() for respuesta in respuestas_usuario]
                        respuestas_usuario_combinadas = ','.join(respuestas_usuario_limpias)  # Une las respuestas sin comillas ni corchetes
                        request.session['respuesta_usuario_revicion'].append({
                            'pregunta_id': pregunta_id,
                            'respuestas_usuario': respuestas_usuario_combinadas  # Guardar las respuestas combinadas
                        })
                        request.session.modified = True
                        print('Respuesta del usuario', respuestas_usuario_combinadas)
                        print(f'Respuesta correcta: {pregunta.respuesta.replace(" ","")}')
                        print('La pregunta es de tipo OM')

                        # Eliminar espacios en blanco y comparar
                        respuestas_usuario_combinadas_limpio = respuestas_usuario_combinadas.replace(" ", "")
                        respuesta_correcta_limpia = pregunta.respuesta.replace(" ", "")

                        if respuestas_usuario_combinadas_limpio == respuesta_correcta_limpia:
                            print('Respuesta correcta')
                            notar += 1
                        else:
                            print('Respuesta incorrecta')
                else:
                    print(f'No se encontró la pregunta con ID: {pregunta_id}')
            print('\n')

        if total_preguntas == 0:
            notar = 0
        else:
            notar = (notar / total_preguntas) * 100

        examen = Examen.objects.create(
            usuario_id=user_id,
            cuestionario=cuestionario,
            completado=True,
            nota=notar
        )
        examen.preguntas.set(preguntas_seleccionadas)
        examen.save()

        return redirect('detalle_examen', examen_id=examen.id)



    
    
def detalle_examen(request, examen_id):
    # Recuperar las preguntas seleccionadas usando los IDs guardados en la sesión
    preguntas_seleccionadas_ids = request.session.get('preguntas_seleccionadas', [])
    preguntas_seleccionadas = Pregunta.objects.filter(id__in=preguntas_seleccionadas_ids)
    
    # Obtener el examen
    examen = get_object_or_404(Examen, id=examen_id)
    
    # Obtener el user_id de la sesión para asociarlo con ExamenRevision
    user_id = request.session.get('user_id')
    usuario = get_object_or_404(Usuario, id=user_id)
    
    # Obtener las respuestas del usuario desde la sesión
    respuestas_usuario = request.session.get('respuesta_usuario_revicion', [])
    print('Respuestas del usuario en la parte del detalle examen:', respuestas_usuario)
    examen_revision_existe = ExamenRevision.objects.filter(examen=examen, usuario=usuario).exists()
    
    # Crear una nueva revisión del examen y almacenar las respuestas del usuario
    if not examen_revision_existe:
        # Crear una nueva revisión del examen y almacenar las respuestas del usuario
        ExamenRevision.objects.create(
            examen=examen,
            usuario=usuario,
            revisado=True,  # Marcamos como revisado
            respuestas_usuario=respuestas_usuario  # Guardar las respuestas del usuario
        )
    
    # Vincular cada pregunta con su respectiva respuesta del usuario
    preguntas_con_respuestas = []
    for pregunta in preguntas_seleccionadas:
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
    

    
    return render(request, 'cliente/detalle_examen.html', {
        'examen': examen,
        'preguntas_con_respuestas': preguntas_con_respuestas
    })
def detalle_examen_terminado(request, examen_revision_id):
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
    
    return render(request, 'cliente/detalle_examen_terminado.html', {
        'examen_revision': examen_revision,
        'preguntas_con_respuestas': preguntas_con_respuestas
    })






try:
    arduino = serial.Serial('COM4', 9600)  # Cambia 'COM3' al puerto donde está conectado tu Arduino
except Exception as e:
    arduino = None
    print(f"Error al conectar con Arduino: {e}")


# Vista para controlar el LED en el pin 5
def control_led_viewc(request):
    return render(request, 'cliente/control_led.html')


# Vista para enviar comandos al LED del pin 5
def control_ledc(request, led, action):
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
def control_leds_viewc(request):
    return render(request, 'cliente/control_leds.html')


# Vista para enviar comandos a los LEDs de los pines 6, 7 y 8
def control_ledsc(request, led, action):
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
def control_ledrgb_viewc(request):
    return render(request, 'cliente/control_ledrgb.html')


# Vista para enviar comandos al LED RGB
def control_ledrgbc(request, led, action):
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
def control_servo_viewc(request):
    return render(request, 'cliente/control_servo.html')

def control_servoc(request, command):
    if arduino:
        try:
            arduino.write(f"{command}\n".encode())  # Enviar comando al Arduino
            return JsonResponse({"status": "success", "command": command})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Arduino no conectado."})

def code_executor_viewc(request):
    return render(request, 'cliente/execute_code.html')

    