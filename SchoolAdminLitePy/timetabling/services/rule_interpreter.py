import re
import unicodedata

from apps.core.models import Subject, Teacher
from timetabling.models import SchedulingRule


DAY_NAMES = {
    "lunes": "LUN",
    "martes": "MAR",
    "miercoles": "MIÉ",
    "jueves": "JUE",
    "viernes": "VIE",
    "sabado": "SÁB",
}


def _normalize(value):
    value = unicodedata.normalize("NFKD", value.lower())
    return "".join(character for character in value if not unicodedata.combining(character))


def _find_teacher(prompt_normalized):
    candidates = []
    for teacher in Teacher.objects.filter(active=True):
        full_name = _normalize(str(teacher))
        name_tokens = [token for token in full_name.split() if len(token) >= 4]
        score = sum(token in prompt_normalized for token in name_tokens)
        if score:
            candidates.append((score, len(full_name), teacher))
    return max(candidates, key=lambda item: (item[0], item[1]), default=(0, 0, None))[2]


def _find_subjects(prompt_normalized, school_year):
    matches = []
    seen_names = set()
    for subject in Subject.objects.filter(section__school_year=school_year, weekly_hours__gt=0):
        normalized_name = _normalize(subject.name)
        if normalized_name in prompt_normalized and normalized_name not in seen_names:
            seen_names.add(normalized_name)
            matches.append(subject)
    return matches


def interpret_predefined_rules(prompt, school_year):
    normalized = _normalize(prompt)
    teacher = _find_teacher(normalized)
    detected = []
    days = [code for name, code in DAY_NAMES.items() if name in normalized]

    negative_availability = any(
        phrase in normalized
        for phrase in ("no puede", "no debe", "no trabaja", "no disponible", "nunca")
    )
    if teacher and days and negative_availability:
        detected.append({
            "name": f"{teacher} no disponible: {', '.join(days)}",
            "rule_type": "teacher_unavailable",
            "severity": SchedulingRule.HARD,
            "weight": 100,
            "parameters": {"teacher_id": teacher.pk, "days": days, "periods": "all"},
            "explanation": "Impide asignar clases al docente durante los días indicados.",
        })

    max_match = re.search(r"(?:maximo|no mas de)\s+(\d+)\s+horas?\s+(?:al|por)\s+(dia|semana)", normalized)
    if teacher and max_match:
        amount = int(max_match.group(1))
        period = max_match.group(2)
        detected.append({
            "name": f"Máximo de {amount} horas por {period} para {teacher}",
            "rule_type": "teacher_max_daily" if period == "dia" else "teacher_max_weekly",
            "severity": SchedulingRule.HARD,
            "weight": 100,
            "parameters": {"teacher_id": teacher.pk, "maximum": amount},
            "explanation": "Limita la carga docente según la instrucción confirmada.",
        })

    if "bloque doble" in normalized or "bloques dobles" in normalized:
        for subject in _find_subjects(normalized, school_year):
            detected.append({
                "name": f"{subject.name} en bloques dobles",
                "rule_type": "lesson_pattern",
                "severity": SchedulingRule.HARD,
                "weight": 100,
                "parameters": {
                    "subject_name": subject.name,
                    "session_length": 2,
                    "allow_cross_break": False,
                },
                "explanation": "Agrupa las horas de la asignatura en sesiones de dos bloques consecutivos.",
            })

    if "hueco" in normalized or "ventana" in normalized:
        detected.append({
            "name": "Minimizar huecos de docentes" + (f" para {teacher}" if teacher else ""),
            "rule_type": "minimize_teacher_gaps",
            "severity": SchedulingRule.SOFT,
            "weight": 80,
            "parameters": {"teacher_id": teacher.pk if teacher else None},
            "explanation": "Penaliza bloques libres entre clases del mismo docente.",
        })

    return detected


def create_proposed_rules(prompt, school_year, source_message, user):
    return [
        SchedulingRule.objects.create(
            school_year=school_year,
            source_message=source_message,
            created_by=user,
            **rule,
        )
        for rule in interpret_predefined_rules(prompt, school_year)
    ]
