from django import forms
from modulos.cliente.models import Usuario, Perfil, EntregaTarea, Pregunta
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
class EntregaTareaForm(forms.ModelForm):
    class Meta:
        model = EntregaTarea
        fields = ['archivo_entregado']
class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['pregunta', 'tipo', 'opciones']
        widgets = {
            'pregunta': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'opciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
class RegistroMateriaForm(forms.Form):
    sigla_materia = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))