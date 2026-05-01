from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_modules", "0002_modulestate_is_installed"),
    ]

    operations = [
        migrations.AddField(
            model_name="modulestate",
            name="module_type",
            field=models.CharField(default="removable", max_length=40),
        ),
        migrations.AddField(
            model_name="modulestate",
            name="removable",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="modulestate",
            name="is_core",
            field=models.BooleanField(default=False),
        ),
    ]
