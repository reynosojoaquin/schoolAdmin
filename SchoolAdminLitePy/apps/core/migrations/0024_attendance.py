import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_remove_section_named_courses"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("date", models.DateField(verbose_name="fecha")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("present", "Presente"),
                            ("absent", "Ausente"),
                            ("late", "Tarde"),
                            ("excused", "Excusa"),
                        ],
                        default="present",
                        max_length=12,
                        verbose_name="estado",
                    ),
                ),
                ("note", models.CharField(blank=True, max_length=160, verbose_name="nota")),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendances",
                        to="core.enrollment",
                        verbose_name="inscripcion",
                    ),
                ),
                (
                    "recorded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="recorded_attendances",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="registrado por",
                    ),
                ),
            ],
            options={
                "verbose_name": "asistencia",
                "verbose_name_plural": "asistencias",
                "ordering": ["-date", "enrollment__student__last_name", "enrollment__student__first_name"],
                "unique_together": {("enrollment", "date")},
            },
        ),
    ]
