from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
def redirect_to_login(request):
    return redirect('login')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('administrador/', include('modulos.administrador.urls')),
    path('cliente/', include('modulos.cliente.urls')),
    # Ruta para la página principal
    path('', include('modulos.cliente.urls')), 
     path('', redirect_to_login), # Ajusta si la página principal es diferente\
    # Rutas de autenticación
    path('cliente/', include('modulos.cliente.urls')),
    path('', include('modulos.cliente.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)