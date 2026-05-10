from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("turnos", "0002_sedeturno_configuracion_sede"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="configuracionturnos",
            constraint=models.UniqueConstraint(
                condition=Q(sede__isnull=False, tipo_tramite__isnull=False),
                fields=("sede", "tipo_tramite"),
                name="turnos_config_sede_tipo_unique",
            ),
        ),
    ]
