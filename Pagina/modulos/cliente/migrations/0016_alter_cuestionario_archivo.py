# Generated by Django 5.1 on 2024-10-11 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0015_examenrevision_respuestas_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuestionario',
            name='archivo',
            field=models.FileField(blank=True, null=True, upload_to='cuestionarios/'),
        ),
    ]
