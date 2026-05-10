from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tramites', '0005_tipotramite_recurso_turnos'),
        ('turnos', '0001_configuracion_turnos'),
    ]

    operations = [
        migrations.CreateModel(
            name='SedeTurno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=160, verbose_name='Nombre')),
                ('direccion', models.CharField(blank=True, max_length=240, verbose_name='Direccion')),
                ('telefono', models.CharField(blank=True, max_length=60, verbose_name='Telefono')),
                ('activo', models.BooleanField(default=True, verbose_name='Activa')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('modificado', models.DateTimeField(auto_now=True)),
                ('tramites_habilitados', models.ManyToManyField(blank=True, related_name='sedes_turno', to='tramites.tipotramite', verbose_name='Tramites habilitados')),
            ],
            options={
                'verbose_name': 'Sede de tramites',
                'verbose_name_plural': 'Sedes de tramites',
                'ordering': ['nombre'],
            },
        ),
        migrations.AddField(
            model_name='configuracionturnos',
            name='sede',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='configuraciones', to='turnos.sedeturno', verbose_name='Sede'),
        ),
        migrations.AddField(
            model_name='configuracionturnos',
            name='tipo_tramite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='configuraciones_turno', to='tramites.tipotramite', verbose_name='Trámite'),
        ),
    ]
