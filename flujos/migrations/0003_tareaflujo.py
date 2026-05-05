from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flujos', '0002_rename_long_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='TareaFlujo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nodo_id', models.CharField(db_index=True, max_length=255, verbose_name='Nodo')),
                ('nombre', models.CharField(max_length=255, verbose_name='Nombre')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('RESUELTA', 'Resuelta'), ('CANCELADA', 'Cancelada')], db_index=True, default='PENDIENTE', max_length=20, verbose_name='Estado')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('fecha_resolucion', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de resolución')),
                ('datos', models.JSONField(default=dict, help_text='Snapshot mínimo del nodo y metadata operativa.', verbose_name='Datos')),
                ('asignado_a', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tareas_flujo_asignadas', to=settings.AUTH_USER_MODEL, verbose_name='Asignado a')),
                ('instancia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tareas', to='flujos.instanciaflujo', verbose_name='Instancia')),
                ('resuelto_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tareas_flujo_resueltas', to=settings.AUTH_USER_MODEL, verbose_name='Resuelto por')),
            ],
            options={
                'verbose_name': 'Tarea de flujo',
                'verbose_name_plural': 'Tareas de flujo',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.AddIndex(
            model_name='tareaflujo',
            index=models.Index(fields=['instancia', 'estado'], name='ix_tareaflujo_inst_estado'),
        ),
        migrations.AddIndex(
            model_name='tareaflujo',
            index=models.Index(fields=['estado', 'asignado_a'], name='ix_tareaflujo_estado_asig'),
        ),
    ]