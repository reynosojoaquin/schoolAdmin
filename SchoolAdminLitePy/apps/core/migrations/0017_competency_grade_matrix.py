from django.db import migrations
from django.db.models import Count


DEFAULT_COMPETENCIES = (
    "Comunicativa",
    "Pensamiento logico, creativo y critico / Resolucion de problemas",
    "Etica y ciudadana / Desarrollo personal y espiritual",
    "Cientifica y tecnologica / Ambiental y de la salud",
)


def seed_subject_competencies(apps, schema_editor):
    Competency = apps.get_model("core", "Competency")
    Subject = apps.get_model("core", "Subject")
    SubjectCompetency = apps.get_model("core", "SubjectCompetency")
    Grade = apps.get_model("core", "Grade")

    for subject in Subject.objects.all().order_by("id"):
        first_subject_competency = None
        for description in DEFAULT_COMPETENCIES:
            competency, _ = Competency.objects.get_or_create(description=description)
            subject_competency, _ = SubjectCompetency.objects.get_or_create(
                subject=subject,
                competency=competency,
            )
            if first_subject_competency is None:
                first_subject_competency = subject_competency
        if first_subject_competency:
            Grade.objects.filter(subject=subject, subject_competency__isnull=True).update(
                subject_competency=first_subject_competency
            )

    duplicate_groups = (
        Grade.objects.values("enrollment_id", "subject_id", "subject_competency_id")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
    )
    for group in duplicate_groups:
        grades = list(
            Grade.objects.filter(
                enrollment_id=group["enrollment_id"],
                subject_id=group["subject_id"],
                subject_competency_id=group["subject_competency_id"],
            ).order_by("id")
        )
        keeper = grades[0]
        for duplicate in grades[1:]:
            changed_fields = []
            for field_name in ("period_1", "period_2", "period_3", "period_4"):
                if getattr(keeper, field_name) is None and getattr(duplicate, field_name) is not None:
                    setattr(keeper, field_name, getattr(duplicate, field_name))
                    changed_fields.append(field_name)
            if changed_fields:
                keeper.save(update_fields=changed_fields)
            duplicate.delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("core", "0016_create_teacher_users"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="grade",
            unique_together=set(),
        ),
        migrations.RunPython(seed_subject_competencies, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name="grade",
            unique_together={("enrollment", "subject", "subject_competency")},
        ),
    ]
