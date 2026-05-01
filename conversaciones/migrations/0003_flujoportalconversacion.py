from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("conversaciones", "0002_conversacion_ciudadano_usuario"),
    ]

    operations = [
        migrations.CreateModel(
            name="FlujoPortalConversacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "canal",
                    models.CharField(
                        choices=[
                            ("reclamo_anonimo", "Reclamo anonimo"),
                            ("reclamo_login", "Reclamo logueado"),
                            ("tramite_login", "Tramite logueado"),
                            ("operador", "Operador"),
                        ],
                        db_index=True,
                        default="reclamo_anonimo",
                        max_length=30,
                    ),
                ),
                (
                    "modulo",
                    models.CharField(
                        blank=True,
                        choices=[("reclamos", "Reclamos"), ("tramites", "Tramites")],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                (
                    "paso",
                    models.CharField(
                        choices=[
                            ("menu", "Menu"),
                            ("seleccion_tipo", "Seleccion de tipo"),
                            ("titulo", "Titulo"),
                            ("descripcion", "Descripcion"),
                            ("confirmacion", "Confirmacion"),
                            ("finalizado", "Finalizado"),
                        ],
                        db_index=True,
                        default="menu",
                        max_length=20,
                    ),
                ),
                ("datos", models.JSONField(blank=True, default=dict)),
                ("derivado_operador", models.BooleanField(db_index=True, default=False)),
                ("finalizado", models.BooleanField(db_index=True, default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "conversacion",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="flujo_portal",
                        to="conversaciones.conversacion",
                    ),
                ),
            ],
            options={
                "verbose_name": "Flujo portal de conversacion",
                "verbose_name_plural": "Flujos portal de conversaciones",
            },
        ),
        migrations.AddIndex(
            model_name="flujoportalconversacion",
            index=models.Index(fields=["canal", "paso"], name="conversacio_canal_8a818f_idx"),
        ),
        migrations.AddIndex(
            model_name="flujoportalconversacion",
            index=models.Index(fields=["modulo", "finalizado"], name="conversacio_modulo_96f82f_idx"),
        ),
    ]
