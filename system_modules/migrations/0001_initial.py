from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ModuleState",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("display_name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("is_enabled", models.BooleanField(default=True)),
                ("depends_on", models.JSONField(blank=True, default=list)),
                ("managed_groups", models.JSONField(blank=True, default=list)),
                ("nav_items", models.JSONField(blank=True, default=list)),
                ("route_handles", models.JSONField(blank=True, default=list)),
                ("api_handles", models.JSONField(blank=True, default=list)),
                ("websocket_handles", models.JSONField(blank=True, default=list)),
                ("startup_hooks", models.JSONField(blank=True, default=list)),
                ("adapter_points", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Module state",
                "verbose_name_plural": "Module states",
                "ordering": ["slug"],
            },
        ),
    ]
