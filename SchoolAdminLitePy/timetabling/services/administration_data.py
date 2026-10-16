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
    SchedulingRule,
)


class ScheduleSetupError(ValueError):
    pass


def _teacher_overload_report(
    teachers: list[dict],
    groups: list[dict],
    blocks: list,
    rules: list[dict],
) -> list[dict]:
    teachers_by_id = {teacher["id"]: teacher for teacher in teachers}
    required_hours: dict[int, int] = defaultdict(int)
    for group in groups:
        for assignment in group.get("materias_asignadas", []):
            teacher_id = assignment.get("profesor_id")
            if teacher_id in teachers_by_id:
                required_hours[teacher_id] += assignment.get("horas_asignadas", 0)

    weekly_limits: dict[int, list[int]] = defaultdict(list)
    daily_limits: dict[int, list[int]] = defaultdict(list)
    unavailable_days: dict[int, set[str]] = defaultdict(set)
    for rule in rules:
        if rule.get("severity") != SchedulingRule.HARD:
            continue
        parameters = rule.get("parameters", {})
        teacher_id = parameters.get("teacher_id")
        if teacher_id not in teachers_by_id:
            continue
        if rule.get("rule_type") == "teacher_max_weekly":
            weekly_limits[teacher_id].append(int(parameters["maximum"]))
        elif rule.get("rule_type") == "teacher_max_daily":
            daily_limits[teacher_id].append(int(parameters["maximum"]))
        elif rule.get("rule_type") == "teacher_unavailable":
            unavailable_days[teacher_id].update(parameters.get("days", []))

    blocks_by_day: dict[str, list[int]] = defaultdict(list)
    for block in blocks:
        day = block["dia"] if isinstance(block, dict) else block.dia
        order = block.get("orden", 0) if isinstance(block, dict) else block.orden
        blocks_by_day[day].append(order)

    report = []
    for teacher_id, teacher in teachers_by_id.items():
        availability = teacher.get("disponibilidad", {})
        if not availability:
            availability = blocks_by_day
        weekly_limit = min([
            teacher.get("horas_max_semana", 24),
            *weekly_limits[teacher_id],
        ])
        daily_limit = min([
            teacher.get("horas_max_dia", 6),
            *daily_limits[teacher_id],
        ])
        available_capacity = sum(
            min(
                daily_limit,
                0 if day in unavailable_days[teacher_id] else len(
                    set(orders) & set(availability.get(day, []))
                ),
            )
            for day, orders in blocks_by_day.items()
        )
        capacity = min(weekly_limit, available_capacity)
        load = required_hours[teacher_id]
        if load > capacity:
            report.append({
                "teacher_id": teacher_id,
                "teacher": teacher.get("nombre", str(teacher_id)),
                "required_hours": load,
                "maximum_weekly_hours": weekly_limit,
                "available_capacity": available_capacity,
            })
    return report


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
    summary_groups = []
    subject_count = 0
    total_hours = 0

    for section in sections:
        active_assignments = {
            assignment.subject_id: assignment
            for assignment in section.teaching_assignments.all()
            if assignment.active and assignment.teacher.active
        }
        summary_groups.append({
            "materias_asignadas": [
                {
                    "profesor_id": assignment.teacher_id,
                    "horas_asignadas": subject.weekly_hours,
                }
                for subject in section.subjects.all()
                if subject.weekly_hours > 0
                and (assignment := active_assignments.get(subject.pk))
            ],
        })
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

    profiles_by_teacher = {
        profile.docente_administracion_id: profile
        for profile in Profesor.objects.filter(
            docente_administracion_id__in=teacher_ids
        )
    }
    confirmed_rules = list(SchedulingRule.objects.filter(
        school_year=school_year,
        status=SchedulingRule.CONFIRMED,
        active=True,
    ).values(
        "rule_type", "severity", "parameters"
    ))
    blocks = list(
        BloqueHorario.objects.filter(activo=True).order_by("dia", "orden")
    )
    summary_teachers = []
    for teacher_id in teacher_ids:
        profile = profiles_by_teacher.get(teacher_id)
        summary_teachers.append({
            "id": teacher_id,
            "nombre": str(next(
                assignment.teacher
                for section in sections
                for assignment in section.teaching_assignments.all()
                if assignment.active
                and assignment.teacher.active
                and assignment.teacher_id == teacher_id
            )),
            "disponibilidad": profile.disponibilidad if profile else {},
            "horas_max_dia": profile.horas_max_dia if profile else 6,
            "horas_max_semana": profile.horas_max_semana if profile else 24,
        })
    teacher_overloads = _teacher_overload_report(
        summary_teachers,
        summary_groups,
        blocks,
        confirmed_rules,
    )
    if teacher_overloads:
        issues.append(
            f"{len(teacher_overloads)} docente(s) superan su capacidad semanal disponible."
        )
    if not blocks_count:
        issues.append("Configura los bloques horarios en Horarios > Recursos y disponibilidad.")
    if not classrooms_count:
        issues.append("Configura las aulas en Horarios > Recursos y disponibilidad.")

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
        "teacher_overloads": teacher_overloads,
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
            "No hay bloques de horario activos. Configúralos en Horarios > Recursos y disponibilidad."
        )
    if not classrooms:
        raise ScheduleSetupError(
            "No hay aulas activas. Configúralas en Horarios > Recursos y disponibilidad."
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
            "disponibilidad": group_by_section[section.pk].disponibilidad,
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

    timetable_subjects_by_admin_id = {
        administrative_id: timetable_subject.pk
        for administrative_id, timetable_subject in subject_by_id.items()
    }
    timetable_subject_ids_by_name: dict[str, list[int]] = defaultdict(list)
    for administrative_subject in subjects:
        timetable_subject_ids_by_name[administrative_subject.name.casefold()].append(
            timetable_subjects_by_admin_id[administrative_subject.pk]
        )

    confirmed_rules = []
    for rule in SchedulingRule.objects.filter(
        school_year=school_year,
        status=SchedulingRule.CONFIRMED,
        active=True,
    ).order_by("created_at", "pk"):
        parameters = dict(rule.parameters)
        if rule.severity not in {SchedulingRule.HARD, SchedulingRule.SOFT}:
            raise ScheduleSetupError(
                f"La regla confirmada «{rule.name}» tiene una severidad no válida."
            )
        if rule.rule_type in {
            "teacher_unavailable",
            "teacher_max_daily",
            "teacher_max_weekly",
        }:
            administrative_teacher_id = parameters.get("teacher_id")
            profile = teacher_by_id.get(administrative_teacher_id)
            if profile is None:
                raise ScheduleSetupError(
                    f"La regla confirmada «{rule.name}» apunta a un docente sin "
                    "asignaciones activas en el año escolar actual."
                )
            parameters["teacher_id"] = profile.pk
            if rule.rule_type in {"teacher_max_daily", "teacher_max_weekly"}:
                maximum = parameters.get("maximum")
                if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 0:
                    raise ScheduleSetupError(
                        f"La regla confirmada «{rule.name}» tiene un máximo de horas no válido."
                    )
            elif (
                not isinstance(parameters.get("days"), list)
                or parameters.get("periods", "all") != "all"
            ):
                raise ScheduleSetupError(
                    f"La regla confirmada «{rule.name}» tiene días o periodos no válidos."
                )
        elif rule.rule_type == "minimize_teacher_gaps":
            administrative_teacher_id = parameters.get("teacher_id")
            if administrative_teacher_id is not None:
                profile = teacher_by_id.get(administrative_teacher_id)
                if profile is None:
                    raise ScheduleSetupError(
                        f"La regla confirmada «{rule.name}» apunta a un docente sin "
                        "asignaciones activas en el año escolar actual."
                    )
                parameters["teacher_id"] = profile.pk
        elif rule.rule_type == "lesson_pattern":
            session_length = parameters.get("session_length")
            if (
                not isinstance(session_length, int)
                or isinstance(session_length, bool)
                or session_length not in (2, 3)
            ):
                raise ScheduleSetupError(
                    f"La regla confirmada «{rule.name}» tiene una longitud de sesión no válida."
                )
            administrative_subject_ids = parameters.get("subject_ids", [])
            if not isinstance(administrative_subject_ids, list):
                raise ScheduleSetupError(
                    f"La regla confirmada «{rule.name}» no identifica sus asignaturas correctamente."
                )
            if administrative_subject_ids:
                parameters["subject_ids"] = [
                    timetable_subjects_by_admin_id[subject_id]
                    for subject_id in administrative_subject_ids
                    if subject_id in timetable_subjects_by_admin_id
                ]
            else:
                subject_name = str(parameters.get("subject_name", "")).casefold()
                parameters["subject_ids"] = timetable_subject_ids_by_name.get(
                    subject_name, []
                )
            if not parameters["subject_ids"]:
                raise ScheduleSetupError(
                    f"La regla confirmada «{rule.name}» apunta a una asignatura "
                    "que ya no está activa en el año escolar actual."
                )
        confirmed_rules.append({
            "id": rule.pk,
            "name": rule.name,
            "rule_type": rule.rule_type,
            "severity": rule.severity,
            "weight": rule.weight,
            "parameters": parameters,
        })

    teacher_overloads = _teacher_overload_report(
        payload_teachers,
        payload_groups,
        blocks,
        confirmed_rules,
    )

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
                "disponibilidad": classroom.disponibilidad,
            }
            for classroom in classrooms
        ],
        "restricciones_personalizadas": [],
        "reglas_confirmadas": confirmed_rules,
        "sobrecargas_docentes": teacher_overloads,
        "tiempo_maximo_segundos": 55.0,
    }
