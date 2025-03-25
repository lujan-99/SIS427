from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.timezone import now
class Usuario(models.Model):
    NIVELES_USUARIO = (
        (0, 'Cliente Normal'),
        (1, 'Admin'),
    )
    nombre = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    nivel = models.IntegerField(choices=NIVELES_USUARIO, default=0)
    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    def __str__(self):
        return f"{self.nombre} ({'Admin' if self.nivel == 1 else 'Cliente Normal'})"
class Perfil(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    apellidos = models.CharField(max_length=150, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    biografia = models.TextField(null=True, blank=True)
    def __str__(self):
        nombre_completo = f"{self.usuario.nombre} {self.apellidos}".strip()
        return f'Perfil de {nombre_completo}' if nombre_completo else f'Perfil de {self.usuario.nombre}'
class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10, unique=True)  # Nuevo campo para la sigla
    usuarios = models.ManyToManyField('Usuario', related_name='materias')

    def __str__(self):
        return f'{self.nombre} ({self.sigla})' 

class Tema(models.Model):
    nombre = models.CharField(max_length=100)
    materia = models.ForeignKey(Materia, related_name='temas', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Contenido(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tema = models.ForeignKey('Tema', related_name='contenidos', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='archivos/', null=True, blank=True)  # Permitir cualquier tipo de archivo

    def __str__(self):
        return self.titulo

class Tarea(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tema = models.ForeignKey(Tema, related_name='tareas', on_delete=models.CASCADE)
    archivo_pdf = models.FileField(upload_to='archivos/tareas/', blank=True, null=True)  # Permitir cualquier tipo de archivo, manteniendo el nombre archivo_pdf

    def __str__(self):
        return self.titulo

class EntregaTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='entregas')
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='entregas')
    archivo_entregado = models.FileField(upload_to='entregas/', blank=False, null=False)  # Permitir cualquier tipo de archivo, manteniendo el nombre archivo_entregado
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    revisado = models.BooleanField(default=False)

    def __str__(self):
        return f"Tarea: {self.tarea.titulo} entregada por {self.usuario.nombre}"
class Pregunta(models.Model):
    OPCIONES_TIPO = [
        ('OM', 'Opción Múltiple'),
        ('FV', 'Falso o Verdadero'),
        ('RL', 'Rellenar'),
    ]

    pregunta = models.TextField()  # Texto de la pregunta
    respuesta = models.TextField()  # Respuesta correcta
    tipo = models.CharField(max_length=2, choices=OPCIONES_TIPO, default='OM')  # Tipo de pregunta
    opciones = models.TextField(blank=True, null=True, help_text="Ingrese las opciones solo si es Opción Múltiple")  # Opciones para tipo OM
    cuestionario = models.ForeignKey('Cuestionario', on_delete=models.CASCADE, related_name='preguntas')  # Relación con Cuestionario

    def __str__(self):
        return f"{self.pregunta} ({self.get_tipo_display()})"

class ClienteLogeado(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='logins')
    fecha_login = models.DateTimeField(default=now)

    def _str_(self):
        return f"{self.usuario.nombre} - {self.fecha_login}"
    

class Examen(models.Model):
    # El id será automático en Django
    preguntas = models.ManyToManyField(Pregunta, related_name='examenes')  # Relación Many-to-Many con Pregunta
    nota = models.IntegerField()  # Nota obtenida en el examen
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='examenes')  # Relación con Usuario
    cuestionario = models.ForeignKey('Cuestionario', on_delete=models.CASCADE, related_name='examenes')  # Relación con Cuestionario
    completado = models.BooleanField(default=False)  # Campo para indicar si el examen está completado (0: no, 1: sí)
    
    def __str__(self):
        return f"Examen de {self.usuario.nombre}, Nota: {self.nota} (Cuestionario: {self.cuestionario.nombre})"


class Cuestionario(models.Model):
    nombre = models.CharField(max_length=200)  # Nombre del cuestionario
    archivo = models.FileField(upload_to='cuestionarios/', blank=True, null=True)  # Campo para subir el archivo (opcional)
    materia = models.ForeignKey('Materia', on_delete=models.CASCADE, related_name='cuestionarios')  # Relación con Materia

    def __str__(self):
        return self.nombre
class ExamenRevision(models.Model):
    examen = models.ForeignKey('Examen', on_delete=models.CASCADE, related_name='entregas_examen')
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='examenes_entregados')
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    revisado = models.BooleanField(default=False)
    respuestas_usuario = models.JSONField(default=list)  # Aquí guardamos la lista de respuestas del usuario

    def __str__(self):
        return f"Examen: {self.examen.id} entregado por {self.usuario.nombre} en {self.fecha_entrega}"
