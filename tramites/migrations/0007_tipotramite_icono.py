from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tramites", "0006_tipotramite_costo_requisitos_info_extra"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipotramite",
            name="icono",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
    ]
