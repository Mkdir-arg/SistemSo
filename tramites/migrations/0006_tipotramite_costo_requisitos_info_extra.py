from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tramites", "0005_tipotramite_recurso_turnos"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipotramite",
            name="costo",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="tipotramite",
            name="informacion_extra",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="tipotramite",
            name="requisitos_info",
            field=models.TextField(blank=True),
        ),
    ]


