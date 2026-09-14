import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("timetabling", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HorarioJob",
            fields=[
                ("job_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("estado", models.CharField(default="pendiente", max_length=20, verbose_name="estado")),
                ("progreso", models.FloatField(default=0.0, verbose_name="progreso")),
                ("mensaje", models.CharField(blank=True, max_length=300, verbose_name="mensaje")),
                ("datos", models.JSONField(blank=True, default=dict, verbose_name="datos de entrada")),
                ("asignaciones", models.JSONField(blank=True, default=list, verbose_name="asignaciones")),
                ("estadisticas", models.JSONField(blank=True, default=dict, verbose_name="estadisticas")),
                ("restricciones_relajadas", models.JSONField(blank=True, default=list, verbose_name="restricciones relajadas")),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "trabajo de generacion de horario",
                "verbose_name_plural": "trabajos de generacion de horarios",
                "ordering": ["-creado_en"],
            },
        ),
    ]
