from django.db import migrations


def remove_general_sections(apps, schema_editor):
    Section = apps.get_model("core", "Section")
    Enrollment = apps.get_model("core", "Enrollment")
    Subject = apps.get_model("core", "Subject")
    Grade = apps.get_model("core", "Grade")
    GradeCompletion = apps.get_model("core", "GradeCompletion")

    general_sections = Section.objects.filter(name__iexact="General").select_related("course").order_by("id")
    for section in general_sections:
        target_section = (
            Section.objects.filter(course_id=section.course_id, school_year=section.school_year)
            .exclude(pk=section.pk)
            .exclude(name__iexact="General")
            .order_by("name", "id")
            .first()
        )
        if target_section:
            Enrollment.objects.filter(section=section).update(section=target_section)

        general_subjects = Subject.objects.filter(section=section)
        if Grade.objects.filter(subject__in=general_subjects).exists():
            raise RuntimeError("No se pueden eliminar secciones General con calificaciones relacionadas.")
        if GradeCompletion.objects.filter(subject__in=general_subjects).exists():
            raise RuntimeError("No se pueden eliminar secciones General con evaluaciones completivas relacionadas.")

        general_subjects.delete()
        if not Enrollment.objects.filter(section=section).exists():
            section.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_carga_horaria_2025_2026"),
    ]

    operations = [
        migrations.RunPython(remove_general_sections, migrations.RunPython.noop),
    ]
