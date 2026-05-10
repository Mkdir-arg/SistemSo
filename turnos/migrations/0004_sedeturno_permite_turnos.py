from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turnos', '0003_configuracionturnos_unique_sede_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='sedeturno',
            name='permite_turnos',
            field=models.BooleanField(default=True, verbose_name='Permite turnos'),
        ),
    ]
