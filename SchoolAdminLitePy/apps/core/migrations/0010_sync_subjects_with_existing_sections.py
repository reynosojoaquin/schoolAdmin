from django.db import migrations


SUBJECTS_BY_GRADE = {
    "1": [
        "Lengua Espa\u00f1ola",
        "Taller de lectoescritura",
        "Ingl\u00e9s",
        "F.I.H.R",
        "Franc\u00e9s",
        "Matem\u00e1ticas",
        "Ciencias Sociales",
        "Moral y C\u00edvica",
        "Ciencias Naturales",
        "Educaci\u00f3n Art\u00edstica",
        "Taller de Artes-BEM",
        "Educaci\u00f3n F\u00edsica",
        "Taller juegos de mesa",
        "Taller de Deporte",
    ],
    "2": [
        "Lengua Espa\u00f1ola",
        "Taller de lectoescritura",
        "Ingl\u00e9s",
        "F.I.H.R",
        "Franc\u00e9s",
        "Taller de Franc\u00e9s",
        "Matem\u00e1ticas",
        "Ciencias Sociales",
        "Moral y C\u00edvica",
        "Ciencias Naturales",
        "Educaci\u00f3n Art\u00edstica",
        "Taller de Artes-BEM",
        "Educaci\u00f3n F\u00edsica",
        "Taller de Deporte",
    ],
    "3": [
        "Lengua Espa\u00f1ola",
        "Ingl\u00e9s",
        "F.I.H.R",
        "Franc\u00e9s",
        "Taller de Franc\u00e9s",
        "Matem\u00e1ticas",
        "Ciencias Sociales",
        "Moral y C\u00edvica",
        "Ciencias Naturales",
        "Educaci\u00f3n Art\u00edstica",
        "Educaci\u00f3n F\u00edsica",
        "Taller juegos de mesa",
        "Taller de Deporte",
    ],
    "4": [
        "Lengua Espa\u00f1ola",
        "Salida de Espa\u00f1ol",
        "Ingl\u00e9s",
        "F.I.H.R",
        "Franc\u00e9s",
        "Matem\u00e1ticas",
        "Ciencias Sociales",
        "Moral y C\u00edvica",
        "Ciencias Naturales",
        "Salida de Ciencias",
        "Educaci\u00f3n Art\u00edstica",
        "Educaci\u00f3n F\u00edsica",
        "Salida",
    ],
    "5": [
        "Lengua Espa\u00f1ola",
        "Salida de Espa\u00f1ol",
        "Ingl\u00e9s",
        "F.I.H.R",
        "Franc\u00e9s",
        "Matem\u00e1ticas",
        "Ciencias Sociales",
        "Moral y C\u00edvica",
        "Ciencias Naturales",
        "Salida de Ciencias",
        "Educaci\u00f3n Art\u00edstica",
        "Educaci\u00f3n F\u00edsica",
        "Salida",
    ],
    "6": [
        "Lengua Espa\u00f1ola",
        "Salida de Espa\u00f1ol",
        "Ingl\u00e9s",
        "F.I.H.R",
        "Franc\u00e9s",
        "Matem\u00e1ticas",
        "Ciencias Sociales",
        "Moral y C\u00edvica",
        "Ciencias Naturales",
        "Salida de Ciencias",
        "Educaci\u00f3n Art\u00edstica",
        "Educaci\u00f3n F\u00edsica",
        "Salida",
    ],
}


GRADE_ALIASES = {
    "1": ["1", "1RO", "1RO.", "1ERO", "PRIMERO"],
    "2": ["2", "2DO", "2DO.", "SEGUNDO"],
    "3": ["3", "3RO", "3RO.", "TERCERO"],
    "4": ["4", "4TO", "4TO.", "CUARTO"],
    "5": ["5", "5TO", "5TO.", "QUINTO"],
    "6": ["6", "6TO", "6TO.", "SEXTO"],
}


def normalize(value):
    return "".join(ch for ch in (value or "").upper().strip() if ch.isalnum())


def grade_from_course_name(name):
    normalized = normalize(name)
    for grade, aliases in GRADE_ALIASES.items():
        if normalized in {normalize(alias) for alias in aliases}:
            return grade
    for char in normalized:
        if char in SUBJECTS_BY_GRADE:
            return char
    return None


def sync_subjects_with_sections(apps, schema_editor):
    Course = apps.get_model("core", "Course")
    Subject = apps.get_model("core", "Subject")

    courses_with_sections = Course.objects.filter(sections__isnull=False).distinct()
    for course in courses_with_sections:
        grade = grade_from_course_name(course.name)
        if not grade:
            continue

        for subject_name in SUBJECTS_BY_GRADE[grade]:
            Subject.objects.get_or_create(course=course, name=subject_name)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_align_personbase_related_names"),
    ]

    operations = [
        migrations.RunPython(sync_subjects_with_sections, migrations.RunPython.noop),
    ]
