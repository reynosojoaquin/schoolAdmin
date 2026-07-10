import django.db.models.deletion
from django.db import migrations, models


def split_course_section(value):
    raw_value = (value or "").strip().upper().replace("-", " ")
    if not raw_value:
        return "", ""
    compact = raw_value.replace(" ", "")
    if len(compact) >= 2 and compact[-1].isalpha() and any(ch.isdigit() for ch in compact[:-1]):
        return compact[:-1], compact[-1]
    parts = raw_value.split()
    if len(parts) >= 2:
        return parts[0], parts[1]
    return raw_value, ""


def migrate_existing_course_sections(apps, schema_editor):
    Course = apps.get_model("core", "Course")
    Section = apps.get_model("core", "Section")
    Enrollment = apps.get_model("core", "Enrollment")

    for course in Course.objects.all():
        course_name, section_name = split_course_section(course.name)
        if not course_name or not section_name:
            continue

        base_course, _ = Course.objects.get_or_create(
            name=course_name,
            defaults={
                "responsible": course.responsible,
                "active": course.active,
            },
        )

        enrollments = Enrollment.objects.filter(course=course)
        for enrollment in enrollments:
            section, _ = Section.objects.get_or_create(
                course=base_course,
                name=section_name,
                school_year=enrollment.school_year,
                defaults={"active": True},
            )
            enrollment.course = base_course
            enrollment.section = section
            enrollment.save(update_fields=["course", "section"])


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("core", "0003_student_sigerd_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Section",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=20, verbose_name="seccion")),
                ("school_year", models.CharField(blank=True, max_length=20, verbose_name="ano escolar")),
                ("active", models.BooleanField(default=True, verbose_name="activa")),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sections",
                        to="core.course",
                        verbose_name="curso",
                    ),
                ),
                (
                    "responsible",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sections",
                        to="core.teacher",
                        verbose_name="docente guia",
                    ),
                ),
            ],
            options={
                "verbose_name": "seccion",
                "verbose_name_plural": "secciones",
                "ordering": ["course__name", "name", "-school_year"],
                "unique_together": {("course", "name", "school_year")},
            },
        ),
        migrations.AddField(
            model_name="enrollment",
            name="section",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="enrollments",
                to="core.section",
                verbose_name="seccion",
            ),
        ),
        migrations.RunPython(migrate_existing_course_sections, migrations.RunPython.noop),
    ]
