from __future__ import annotations

from collections import defaultdict

from django.db import transaction
from django.db.models import Count, Q

from apps.core.models import (
    Section as AdministrativeSection,
    Subject as AdministrativeSubject,
    SystemConfiguration,
    TeachingAssignment,
)
from timetabling.models import (
    AsignacionMateriaGrupo,
    Aula,
    BloqueHorario,
    Grupo,
    Materia,
    Profesor,
)


class ScheduleSetupError(ValueError):
    pass


def _current_school_year() -> str:
    return (
        SystemConfiguration.objects.filter(pk=1)
        .values_list("current_school_year", flat=True)
        .first()
        or ""
    )


def get_administration_summary() -> dict:
    school_year = _current_school_year()
    sections = list(
        AdministrativeSection.objects.filter(
            active=True,
            course__active=True,
            school_year=school_year,
        )
        .select_related("course")
        .prefetch_related("subjects", "teaching_assignments__teacher")
    )
    section_summaries = []
    missing_assignments = []
    teacher_ids = set()
    subject_count = 0
    total_hours = 0

    for section in sections:
        active_assignments = {
            assignment.subject_id: assignment
            for assignment in section.teaching_assignments.all()
            if assignment.active and assignment.teacher.active
        }
        subject_summaries = []
        for subject in section.subjects.all():
            if subject.weekly_hours <= 0:
                continue
            subject_count += 1
            total_hours += subject.weekly_hours
            assignment = active_assignments.get(subject.pk)
            teacher_name = str(assignment.teacher) if assignment else ""
            if assignment:
                teacher_ids.add(assignment.teacher_id)
            else:
                missing_assignments.append(f"{section.course.name} {section.name}: {subject.name}")
            subject_summaries.append({
                "name": subject.name,
                "weekly_hours": subject.weekly_hours,
                "teacher": teacher_name,
                "teacher_id": assignment.teacher_id if assignment else None,
            })
        section_summaries.append({
            "course": section.course.name,
            "name": section.name,
            "school_year": section.school_year,
            "subjects": subject_summaries,
        })

    blocks_count = BloqueHorario.objects.filter(activo=True).count()
    classrooms_count = Aula.objects.filter(activa=True).count()
    issues = []
    if not school_year:
        issues.append("Configura el año escolar actual en la administración.")
    if not sections:
        issues.append(f"No hay secciones activas para el año escolar {school_year or 'actual'}.")
    if not subject_count:
        issues.append("Las secciones del año actual no tienen asignaturas con horas semanales.")
    if missing_assignments:
        issues.append(
            f"Falta asignar docente a {len(missing_assignments)} asignatura(s) activa(s)."
        )
    if not blocks_count:
        issues.append("Configura los bloques de horario en Administración > Horarios.")
    if not classrooms_count:
        issues.append("Configura las aulas en Administración > Horarios.")

    return {
        "school_year": school_year,
        "sections": section_summaries,
        "section_count": len(sections),
        "subject_count": subject_count,
        "teacher_count": len(teacher_ids),
        "total_hours": total_hours,
        "block_count": blocks_count,
        "classroom_count": classrooms_count,
        "missing_assignments": missing_assignments,
        "issues": issues,
        "ready": not issues,
    }


@transaction.atomic
def sync_administration_catalogs() -> dict:
    school_year = _current_school_year()
    if not school_year:
        raise ScheduleSetupError("Configura el año escolar actual en la administración.")

    sections = list(
        AdministrativeSection.objects.filter(
            active=True,
            course__active=True,
            school_year=school_year,
        )
        .select_related("course")
        .annotate(
            active_enrollment_count=Count(
                "enrollments",
                filter=Q(enrollments__active=True),
                distinct=True,
            )
        )
        .prefetch_related("subjects")
    )
    if not sections:
        raise ScheduleSetupError(
            f"No hay secciones activas para el año escolar {school_year}."
        )

    section_ids = [section.pk for section in sections]
    subjects = list(
        AdministrativeSubject.objects.filter(
            section_id__in=section_ids,
            weekly_hours__gt=0,
        ).select_related("section", "section__course")
    )
    if not subjects:
        raise ScheduleSetupError(
            f"Las secciones de {school_year} no tienen asignaturas con horas semanales."
        )

    assignments = list(
        TeachingAssignment.objects.filter(
            active=True,
            section_id__in=section_ids,
            subject_id__in=[subject.pk for subject in subjects],
            teacher__active=True,
        ).select_related("teacher", "subject", "section")
    )
    assignment_by_subject = {assignment.subject_id: assignment for assignment in assignments}
    missing_assignments = [
        f"{subject.section.course.name} {subject.section.name}: {subject.name}"
        for subject in subjects
        if subject.pk not in assignment_by_subject
    ]
    if missing_assignments:
        raise ScheduleSetupError(
            "Asigna docentes activos desde Administración > Asignaciones docentes antes "
            "de generar el horario: " + "; ".join(missing_assignments)
        )

    blocks = list(BloqueHorario.objects.filter(activo=True).order_by("dia", "orden"))
    classrooms = list(Aula.objects.filter(activa=True).order_by("nombre"))
    if not blocks:
        raise ScheduleSetupError(
            "No hay bloques de horario activos. Configúralos en Administración > Horarios."
        )
    if not classrooms:
        raise ScheduleSetupError(
            "No hay aulas activas. Configúralas en Administración > Horarios."
        )

    group_by_section = {}
    for section in sections:
        group, _ = Grupo.objects.update_or_create(
            seccion_administracion=section,
            defaults={
                "nombre": section.name,
                "grado": section.course.name,
                "activo": True,
            },
        )
        group_by_section[section.pk] = group

    subject_by_id = {}
    for subject in subjects:
        timetable_subject, _ = Materia.objects.update_or_create(
            asignatura_administracion=subject,
            defaults={
                "nombre": subject.name,
                "horas_semanales_requeridas": subject.weekly_hours,
                "activa": True,
            },
        )
        subject_by_id[subject.pk] = timetable_subject

    teacher_by_id = {}
    assigned_subjects_by_teacher: dict[int, set[Materia]] = defaultdict(set)
    for assignment in assignments:
        administrative_teacher = assignment.teacher
        default_availability = {
            day: [block.orden for block in blocks if block.dia == day]
            for day in {block.dia for block in blocks}
        }
        profile, _ = Profesor.objects.get_or_create(
            docente_administracion=administrative_teacher,
            defaults={
                "nombre": str(administrative_teacher),
                "disponibilidad": default_availability,
            },
        )
        if profile.nombre != str(administrative_teacher) or not profile.activo:
            profile.nombre = str(administrative_teacher)
            profile.activo = True
            profile.save(update_fields=["nombre", "activo", "updated_at"])
        if not profile.disponibilidad:
            profile.disponibilidad = default_availability
            profile.save(update_fields=["disponibilidad", "updated_at"])
        teacher_by_id[administrative_teacher.pk] = profile
        timetable_subject = subject_by_id[assignment.subject_id]
        assigned_subjects_by_teacher[administrative_teacher.pk].add(timetable_subject)

    for teacher_id, profile in teacher_by_id.items():
        profile.materias_habilitadas.set(assigned_subjects_by_teacher[teacher_id])

    payload_groups = []
    for subject in subjects:
        group = group_by_section[subject.section_id]
        timetable_subject = subject_by_id[subject.pk]
        AsignacionMateriaGrupo.objects.update_or_create(
            grupo=group,
            materia=timetable_subject,
            defaults={"horas_asignadas": subject.weekly_hours},
        )

    for section in sections:
        group = group_by_section[section.pk]
        section_assignments = [
            subject for subject in subjects if subject.section_id == section.pk
        ]
        payload_groups.append({
            "id": group.pk,
            "nombre": f"{section.course.name} {section.name}",
            "grado": section.course.name,
            "cantidad_estudiantes": section.active_enrollment_count,
            "materias_asignadas": [
                {
                    "materia_id": subject_by_id[subject.pk].pk,
                    "horas_asignadas": subject.weekly_hours,
                    "profesor_id": teacher_by_id[
                        assignment_by_subject[subject.pk].teacher_id
                    ].pk,
                }
                for subject in section_assignments
            ],
        })

    payload_teachers = []
    for teacher_id, profile in teacher_by_id.items():
        subject_ids = assigned_subjects_by_teacher[teacher_id]
        payload_teachers.append({
            "id": profile.pk,
            "nombre": profile.nombre,
            "materias_ids": [subject.pk for subject in subject_ids],
            "disponibilidad": profile.disponibilidad,
            "horas_max_dia": profile.horas_max_dia,
            "horas_max_semana": profile.horas_max_semana,
        })

    return {
        "bloques": [
            {
                "id": block.pk,
                "dia": block.dia,
                "hora_inicio": block.hora_inicio.strftime("%H:%M"),
                "hora_fin": block.hora_fin.strftime("%H:%M"),
                "orden": block.orden,
            }
            for block in blocks
        ],
        "profesores": payload_teachers,
        "materias": [
            {
                "id": subject.pk,
                "nombre": subject.nombre,
                "horas_semanales_requeridas": subject.horas_semanales_requeridas,
            }
            for subject in subject_by_id.values()
        ],
        "grupos": payload_groups,
        "aulas": [
            {
                "id": classroom.pk,
                "nombre": classroom.nombre,
                "tipo": classroom.tipo,
                "capacidad": classroom.capacidad,
            }
            for classroom in classrooms
        ],
        "restricciones_personalizadas": [],
        "tiempo_maximo_segundos": 55.0,
    }
