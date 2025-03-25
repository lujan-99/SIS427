from django import forms
from modulos.cliente.models import Usuario, Perfil, Materia, Tema, Contenido, Tarea, Cuestionario, Pregunta
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre' ,'email', 'password', 'nivel']
        widgets = {
            'password': forms.PasswordInput()
        }
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['apellidos', 'fecha_nacimiento', 'direccion', 'telefono', 'biografia']
class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['nombre', 'sigla']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la materia'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sigla'}),
        }

class TemaForm(forms.ModelForm):
    class Meta:
        model = Tema
        fields = ['nombre']
class ContenidoForm(forms.ModelForm):
    class Meta:
        model = Contenido
        fields = ['titulo', 'descripcion', 'archivo']  # Incluye el archivo PDF aquí

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'archivo_pdf']
class CuestionarioForm(forms.ModelForm):
    class Meta:
        model = Cuestionario  # El modelo que queremos usar
        fields = ['nombre', 'archivo']  # Los campos que incluimos en el formulario
class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['pregunta', 'tipo', 'respuesta', 'opciones']
        widgets = {
            'pregunta': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control', 'id': 'id_tipo'}),
            'respuesta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la(s) letra(s) de la(s) respuesta(s), ej: A, B'}),
            'opciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese una opción por línea con el Inciso por delante. Ejemplo:\nA)Sensores\nB)Protocolos de comunicación\nC)Inteligencia Artificial\nD)Realidad Virtual', 'id': 'id_opciones'}),
        }