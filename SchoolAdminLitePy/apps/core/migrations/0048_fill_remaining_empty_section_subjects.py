from django.db import migrations


def fill_remaining_empty_sections(apps, schema_editor):
    Section = apps.get_model("core", "Section")
    Subject = apps.get_model("core", "Subject")
    SubjectCompetency = apps.get_model("core", "SubjectCompetency")

    for section in Section.objects.order_by("school_year", "course_id", "name", "pk"):
        if Subject.objects.filter(section_id=section.pk).exists():
            continue
        source_section = (
            Section.objects.filter(
                course_id=section.course_id,
                school_year__lt=section.school_year,
                subjects__isnull=False,
            )
            .distinct()
            .order_by("-school_year", "name", "-pk")
            .first()
        )
        if not source_section:
            continue
        for source_subject in Subject.objects.filter(section_id=source_section.pk).order_by("pk"):
            subject = Subject.objects.create(
                section_id=section.pk,
                name=source_subject.name,
                weekly_hours=source_subject.weekly_hours,
                responsible_id=source_subject.responsible_id,
            )
            competency_ids = SubjectCompetency.objects.filter(subject_id=source_subject.pk).values_list(
                "competency_id", flat=True
            )
            SubjectCompetency.objects.bulk_create(
                [SubjectCompetency(subject_id=subject.pk, competency_id=competency_id) for competency_id in competency_ids],
                ignore_conflicts=True,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0047_copy_subjects_to_empty_current_sections"),
    ]

    operations = [
        migrations.RunPython(fill_remaining_empty_sections, migrations.RunPython.noop),
    ]
