# Generated by Django 5.1 on 2024-10-10 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0009_remove_examen_materia'),
    ]

    operations = [
        migrations.AddField(
            model_name='pregunta',
            name='opciones',
            field=models.TextField(blank=True, help_text='Ingrese las opciones solo si es Opción Múltiple', null=True),
        ),
    ]
