from django.db import migrations, models
import django.db.models.deletion


def get_general_section(Section, course_id, school_year=""):
    section, _ = Section.objects.get_or_create(
        course_id=course_id,
        name="General",
        school_year=school_year or "",
        defaults={"active": True},
    )
    return section


def update_grade_subject(Grade, grade, target_subject, subject_competency_id):
    existing = (
        Grade.objects.filter(
            enrollment_id=grade.enrollment_id,
            subject_id=target_subject.id,
            subject_competency_id=subject_competency_id,
        )
        .exclude(pk=grade.pk)
        .first()
    )
    if existing:
        changed_fields = []
        for field_name in ("period_1", "period_2", "period_3", "period_4"):
            if getattr(existing, field_name) is None and getattr(grade, field_name) is not None:
                setattr(existing, field_name, getattr(grade, field_name))
                changed_fields.append(field_name)
        if changed_fields:
            existing.save(update_fields=changed_fields)
        grade.delete()
        return

    grade.subject_id = target_subject.id
    grade.subject_competency_id = subject_competency_id
    grade.save(update_fields=["subject", "subject_competency"])


def update_completion_subject(GradeCompletion, completion, target_subject):
    existing = (
        GradeCompletion.objects.filter(enrollment_id=completion.enrollment_id, subject_id=target_subject.id)
        .exclude(pk=completion.pk)
        .first()
    )
    if existing:
        changed_fields = []
        for field_name in (
            "cf",
            "cf_50",
            "cef",
            "cef_50",
            "ccf",
            "ccf_30",
            "ceex",
            "ceex_70",
            "cexf",
            "special_cf",
            "special_ce",
            "approved",
            "reproved",
        ):
            if getattr(existing, field_name) in (None, "") and getattr(completion, field_name) not in (None, ""):
                setattr(existing, field_name, getattr(completion, field_name))
                changed_fields.append(field_name)
        if changed_fields:
            existing.save(update_fields=changed_fields)
        completion.delete()
        return

    completion.subject_id = target_subject.id
    completion.save(update_fields=["subject"])


def copy_competencies(SubjectCompetency, source_subject, target_subject):
    competency_map = {}
    for subject_competency in SubjectCompetency.objects.filter(subject_id=source_subject.id):
        if source_subject.id == target_subject.id:
            competency_map[subject_competency.id] = subject_competency.id
            continue
        target_competency, _ = SubjectCompetency.objects.get_or_create(
            subject_id=target_subject.id,
            competency_id=subject_competency.competency_id,
        )
        competency_map[subject_competency.id] = target_competency.id
    return competency_map


def move_subjects_to_sections(apps, schema_editor):
    Section = apps.get_model("core", "Section")
    Subject = apps.get_model("core", "Subject")
    SubjectCompetency = apps.get_model("core", "SubjectCompetency")
    TeachingAssignment = apps.get_model("core", "TeachingAssignment")
    Enrollment = apps.get_model("core", "Enrollment")
    Grade = apps.get_model("core", "Grade")
    GradeCompletion = apps.get_model("core", "GradeCompletion")

    for enrollment in Enrollment.objects.filter(section__isnull=True).select_related("course"):
        enrollment.section = get_general_section(Section, enrollment.course_id, enrollment.school_year)
        enrollment.save(update_fields=["section"])

    for subject in list(Subject.objects.all().order_by("id")):
        section_ids = list(
            TeachingAssignment.objects.filter(subject_id=subject.id)
            .values_list("section_id", flat=True)
            .distinct()
        )
        grade_section_ids = list(
            Grade.objects.filter(subject_id=subject.id, enrollment__section__isnull=False)
            .values_list("enrollment__section_id", flat=True)
            .distinct()
        )
        completion_section_ids = list(
            GradeCompletion.objects.filter(subject_id=subject.id, enrollment__section__isnull=False)
            .values_list("enrollment__section_id", flat=True)
            .distinct()
        )
        section_ids = list(dict.fromkeys(section_ids + grade_section_ids + completion_section_ids))

        if not section_ids:
            first_section_id = (
                Section.objects.filter(course_id=subject.course_id, active=True)
                .order_by("school_year", "name", "id")
                .values_list("id", flat=True)
                .first()
            )
            if not first_section_id:
                first_section_id = get_general_section(Section, subject.course_id).id
            section_ids = [first_section_id]

        target_by_section = {}
        for index, section_id in enumerate(section_ids):
            if index == 0:
                subject.section_id = section_id
                subject.save(update_fields=["section"])
                target_subject = subject
            else:
                target_subject, _ = Subject.objects.get_or_create(
                    section_id=section_id,
                    name=subject.name,
                    defaults={
                        "course_id": subject.course_id,
                        "responsible_id": subject.responsible_id,
                    },
                )
            target_by_section[section_id] = target_subject

        for section_id, target_subject in target_by_section.items():
            competency_map = copy_competencies(SubjectCompetency, subject, target_subject)

            for assignment in TeachingAssignment.objects.filter(subject_id=subject.id, section_id=section_id):
                duplicate = (
                    TeachingAssignment.objects.filter(section_id=section_id, subject_id=target_subject.id)
                    .exclude(pk=assignment.pk)
                    .first()
                )
                if duplicate:
                    assignment.delete()
                    continue
                assignment.subject_id = target_subject.id
                assignment.save(update_fields=["subject"])

            for grade in Grade.objects.filter(subject_id=subject.id, enrollment__section_id=section_id):
                target_competency_id = competency_map.get(grade.subject_competency_id)
                update_grade_subject(Grade, grade, target_subject, target_competency_id)

            for completion in GradeCompletion.objects.filter(subject_id=subject.id, enrollment__section_id=section_id):
                update_completion_subject(GradeCompletion, completion, target_subject)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("core", "0018_grade_completion"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="section",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subjects",
                to="core.section",
                verbose_name="seccion",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="subject",
            unique_together=set(),
        ),
        migrations.RunPython(move_subjects_to_sections, noop_reverse),
        migrations.AlterField(
            model_name="subject",
            name="section",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subjects",
                to="core.section",
                verbose_name="seccion",
            ),
        ),
        migrations.RemoveField(
            model_name="subject",
            name="course",
        ),
        migrations.AlterModelOptions(
            name="subject",
            options={
                "ordering": ["section__course__name", "section__name", "name"],
                "verbose_name": "asignatura",
                "verbose_name_plural": "asignaturas",
            },
        ),
        migrations.AlterUniqueTogether(
            name="subject",
            unique_together={("section", "name")},
        ),
        migrations.AlterField(
            model_name="enrollment",
            name="section",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="enrollments",
                to="core.section",
                verbose_name="seccion",
            ),
        ),
    ]
