from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0003_rename_portal_turn_ciudada_idx_portal_turn_ciudada_8d9dee_idx_and_more"),
        ("tramites", "0004_tipotramite_portada_destacado"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipotramite",
            name="recurso_turnos",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="tipos_tramite",
                to="portal.recursoturnos",
            ),
        ),
    ]
