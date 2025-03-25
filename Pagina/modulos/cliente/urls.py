from . import views
from django.urls import path
urlpatterns = [
    path('cliente-principal/', views.cliente_principal, name='cliente_principal'),
    path('detalle-usuario/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario_alumno'),
    #Editar Perfil
    path('editar-perfil/<int:usuario_id>/', views.edit_profile, name='edit_profile_estudiante'),
    #Editar Usuario
    path('editar-usuario/<int:usuario_id>/', views.edit_user, name='edit_user_estuidante'),
    #Detalle materia
    path('detalle-materia/<int:materia_id>/', views.detalle_materia, name='detalle_materia_alumno'),
    #Agregar tarea
    path('alumno/tarea/<int:tarea_id>/nueva/', views.agregar_tarea, name='agregar_tarea_alumno'),
    #tomar examen 
    path('alumno/examen/<int:cuestionario_id>/tomar/', views.tomar_examen, name='tomar_examen'),
    path('examen/<int:examen_id>/detalle/', views.detalle_examen, name='detalle_examen'),
    path('examen_revision/<int:examen_revision_id>/', views.detalle_examen_terminado, name='detalle_examen_terminado'),

    path('registro-materia/', views.registro_materia, name='registro_materia'),

    path('cliente/control-led/', views.control_led_viewc, name='control_led_viewc'),  # Ruta para la interfaz de control
    path('cliente/control-led/<str:led>/<str:action>/', views.control_ledc, name='control_ledc'),  # Ruta para controlar LEDs

    path('cliente/control-leds/', views.control_leds_viewc, name='control_leds_viewc'),  # Ruta para la interfaz de control
    path('cliente/control-leds/<str:led>/<str:action>/', views.control_ledsc, name='controls_ledc'),  # Ruta para controlar LEDs

    path('cliente/control-ledrgb/', views.control_ledrgb_viewc, name='control_ledrgb_viewc'),  # Ruta para la interfaz de control
    path('cliente/control-ledrgb/<str:led>/<str:action>/', views.control_ledrgbc, name='controls_ledrgbc'),  # Ruta para controlar LEDs

    path('cliente/control_servo_view/', views.control_servo_viewc, name='control_servo_viewc'),
    path('cliente/control-servo/<str:command>/', views.control_servoc, name='control_servoc'),

# Código ejecutable
    path('cliente/programar/', views.code_executor_viewc, name='code_executor_viewc'),

]