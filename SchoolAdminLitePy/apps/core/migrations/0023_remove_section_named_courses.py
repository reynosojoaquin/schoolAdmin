from django.db import migrations


SECTION_NAMED_COURSES = ("1A", "1B", "1C", "1D")


def remove_section_named_courses(apps, schema_editor):
    Course = apps.get_model("core", "Course")

    for course in Course.objects.filter(name__in=SECTION_NAMED_COURSES):
        if course.sections.exists() or course.enrollments.exists():
            continue
        course.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_student_enrollment_flags"),
    ]

    operations = [
        migrations.RunPython(remove_section_named_courses, migrations.RunPython.noop),
    ]
