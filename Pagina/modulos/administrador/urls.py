from . import views
from django.urls import path
urlpatterns = [

    path('', views.login_view, name='login'),
    path('admin-principal/', views.admin_principal, name='admin_principal'),
    path('lista-usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('administrador/detalle-usuario/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    #Editar Perfi
    path('editar-perfil/<int:usuario_id>/', views.edit_profile, name='edit_profile_admin'),
    #edtitar Usuario
    path('editar-usuario/<int:usuario_id>/', views.edit_user, name='edit_user'),
    path('crear-usuario/', views.create_user, name='create_user'),
    path('crear-perfil/<int:usuario_id>/', views.create_profile, name='create_profile'),
    #cerrar sesion
    path('logout/', views.logout_view, name='logout'),
    #detalle materria admin
    path('detalle-materia/<int:materia_id>/', views.detalle_materia, name='detalle_materia_admin'),
    #
    path('agregar-materia/', views.agregar_materia, name='agregar_materia'),

    #tema materia
    path('agregar-tema/<int:materia_id>/', views.agregar_tema, name='agregar_tema'),
    path('tema/<int:tema_id>/editar/', views.editar_tema, name='editar_tema'),
    path('tema/<int:tema_id>/eliminar/', views.eliminar_tema, name='eliminar_tema'),


    #Contenido
    path('tema/<int:tema_id>/contenido/nuevo/', views.agregar_contenido, name='agregar_contenido'),
    path('contenido/<int:contenido_id>/editar/', views.editar_contenido, name='editar_contenido'),
    path('contenido/<int:contenido_id>/eliminar/', views.eliminar_contenido, name='eliminar_contenido'),

    #tarea
    path('tema/<int:tema_id>/tarea/nueva/', views.agregar_tarea, name='agregar_tarea'),
    path('tarea/<int:tarea_id>/editar/', views.editar_tarea, name='editar_tarea'),
    path('tarea/<int:tarea_id>/eliminar/', views.eliminar_tarea, name='eliminar_tarea'),
    path('tarea/<int:tarea_id>/entregas/', views.lista_usuarios_entregaron_tarea, name='lista_usuarios_entregaron_tarea'),
    path('toggle-revisado/', views.toggle_revisado, name='toggle_revisado'),

    #cuestionario
    path('administrador/cuestionario/nuevo/<int:materia_id>/', views.crear_cuestionario, name='crear_cuestionario'),
    path('cuestionario/<int:cuestionario_id>/entregas/', views.lista_usuarios_entregaron_cuestionario, name='lista_usuarios_entregaron_cuestionario'),
    path('cuestionario/<int:cuestionario_id>/pregunta/agregar/', views.agregar_pregunta, name='agregar_pregunta'),
    # En urls.py
    path('administrador/admin/examen_revision/<int:examen_revision_id>/', views.detalle_examen_terminado_admin, name='detalle_examen_terminado_admin'),



    #pregunta
    path('cuestionario/<int:cuestionario_id>/generar-pregunta/', views.generar_pregunta, name='generar_pregunta'),


    #led
    path('control-led/', views.control_led_view, name='control_led_view'),  # Ruta para la interfaz de control
    path('control-led/<str:led>/<str:action>/', views.control_led, name='control_led'),  # Ruta para controlar LEDs

    path('control-leds/', views.control_leds_view, name='control_leds_view'),  # Ruta para la interfaz de control
    path('control-leds/<str:led>/<str:action>/', views.control_leds, name='controls_led'),  # Ruta para controlar LEDs

    path('control-ledrgb/', views.control_ledrgb_view, name='control_ledrgb_view'),  # Ruta para la interfaz de control
    path('control-ledrgb/<str:led>/<str:action>/', views.control_ledrgb, name='controls_ledrgb'),  # Ruta para controlar LEDs

    path('control_servo_view/', views.control_servo_view, name='control_servo_view'),
    path('control-servo/<str:command>/', views.control_servo, name='control_servo'),

# Código ejecutable
    path('programar/', views.code_executor_view, name='code_executor_view'),
    
]