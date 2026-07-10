import random

from django.db import migrations


def assign_subjects_to_sections(apps, schema_editor):
    Section = apps.get_model("core", "Section")
    Subject = apps.get_model("core", "Subject")
    Teacher = apps.get_model("core", "Teacher")
    TeachingAssignment = apps.get_model("core", "TeachingAssignment")

    teachers = list(Teacher.objects.filter(active=True).order_by("last_name", "first_name", "id"))
    if not teachers:
        return

    rng = random.Random(20252026)

    sections = Section.objects.filter(active=True).select_related("course").order_by(
        "course__name",
        "name",
        "school_year",
        "id",
    )
    for section in sections:
        subjects = Subject.objects.filter(course=section.course).select_related("responsible").order_by("name", "id")
        for subject in subjects:
            teacher = subject.responsible or rng.choice(teachers)
            TeachingAssignment.objects.get_or_create(
                section=section,
                subject=subject,
                defaults={
                    "teacher": teacher,
                    "active": True,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_assign_random_academic_responsibles"),
    ]

    operations = [
        migrations.RunPython(assign_subjects_to_sections, migrations.RunPython.noop),
    ]
