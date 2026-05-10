from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0004_turnociudadano_reprogramacion_relaciones"),
    ]

    operations = [
        migrations.AlterField(
            model_name="turnociudadano",
            name="estado",
            field=models.CharField(
                choices=[
                    ("PENDIENTE", "Pendiente de confirmación"),
                    ("CONFIRMADO", "Confirmado"),
                    ("CANCELADO_CIU", "Cancelado por el ciudadano"),
                    ("CANCELADO_SIS", "Cancelado por el sistema"),
                    ("REPROG_CIU", "Modificado por el ciudadano"),
                    ("REPROG_SIS", "Modificado por el sistema"),
                    ("COMPLETADO", "Completado"),
                ],
                default="PENDIENTE",
                max_length=20,
                verbose_name="Estado",
            ),
        ),
    ]
