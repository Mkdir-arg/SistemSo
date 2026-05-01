from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system_modules", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="modulestate",
            name="is_installed",
            field=models.BooleanField(default=True),
        ),
    ]
