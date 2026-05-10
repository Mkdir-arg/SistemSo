from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0003_rename_portal_turn_ciudada_idx_portal_turn_ciudada_8d9dee_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="turnociudadano",
            name="reemplaza_turno",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="turnos_nuevos_por_reprogramacion",
                to="portal.turnociudadano",
                verbose_name="Reemplaza turno",
            ),
        ),
        migrations.AddField(
            model_name="turnociudadano",
            name="reemplazado_por_turno",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="turnos_anteriores_reprogramados",
                to="portal.turnociudadano",
                verbose_name="Reemplazado por turno",
            ),
        ),
    ]
