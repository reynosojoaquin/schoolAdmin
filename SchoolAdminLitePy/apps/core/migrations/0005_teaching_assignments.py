import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_sections"),
    ]

    operations = [
        migrations.CreateModel(
            name="TeachingAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("active", models.BooleanField(default=True, verbose_name="activa")),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teaching_assignments",
                        to="core.section",
                        verbose_name="seccion",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teaching_assignments",
                        to="core.subject",
                        verbose_name="asignatura",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="teaching_assignments",
                        to="core.teacher",
                        verbose_name="docente",
                    ),
                ),
            ],
            options={
                "verbose_name": "asignacion docente",
                "verbose_name_plural": "asignaciones docentes",
                "ordering": ["section__course__name", "section__name", "subject__name"],
                "unique_together": {("section", "subject")},
            },
        ),
    ]
