import random

from django.db import migrations


def assign_random_responsibles(apps, schema_editor):
    Course = apps.get_model("core", "Course")
    Subject = apps.get_model("core", "Subject")
    Teacher = apps.get_model("core", "Teacher")

    teachers = list(Teacher.objects.filter(active=True).order_by("last_name", "first_name", "id"))
    if not teachers:
        return

    rng = random.Random(20252026)

    for course in Course.objects.filter(active=True).order_by("name", "id"):
        if not course.responsible_id:
            course.responsible = rng.choice(teachers)
            course.save(update_fields=["responsible", "updated_at"])

    for subject in Subject.objects.select_related("course").order_by("course__name", "name", "id"):
        if not subject.responsible_id:
            subject.responsible = rng.choice(teachers)
            subject.save(update_fields=["responsible", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_seed_teachers_from_staff_doc"),
    ]

    operations = [
        migrations.RunPython(assign_random_responsibles, migrations.RunPython.noop),
    ]
