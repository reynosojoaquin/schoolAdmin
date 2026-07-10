from django.db import migrations


COURSE_ALIASES = {
    "1": ["1", "1RO", "1RO.", "1ERO", "PRIMERO"],
    "2": ["2", "2DO", "2DO.", "SEGUNDO"],
    "3": ["3", "3RO", "3RO.", "TERCERO"],
    "4": ["4", "4TO", "4TO.", "CUARTO"],
    "5": ["5", "5TO", "5TO.", "QUINTO"],
    "6": ["6", "6TO", "6TO.", "SEXTO"],
}


SUBJECTS_BY_COURSE = {
    "1": [
        "Lengua Española",
        "Taller de lectoescritura",
        "Inglés",
        "F.I.H.R",
        "Francés",
        "Matemáticas",
        "Ciencias Sociales",
        "Moral y Cívica",
        "Ciencias Naturales",
        "Educación Artística",
        "Taller de Artes-BEM",
        "Educación Física",
        "Taller juegos de mesa",
        "Taller de Deporte",
    ],
    "2": [
        "Lengua Española",
        "Taller de lectoescritura",
        "Inglés",
        "F.I.H.R",
        "Francés",
        "Taller de Francés",
        "Matemáticas",
        "Ciencias Sociales",
        "Moral y Cívica",
        "Ciencias Naturales",
        "Educación Artística",
        "Taller de Artes-BEM",
        "Educación Física",
        "Taller de Deporte",
    ],
    "3": [
        "Lengua Española",
        "Inglés",
        "F.I.H.R",
        "Francés",
        "Taller de Francés",
        "Matemáticas",
        "Ciencias Sociales",
        "Moral y Cívica",
        "Ciencias Naturales",
        "Educación Artística",
        "Educación Física",
        "Taller juegos de mesa",
        "Taller de Deporte",
    ],
    "4": [
        "Lengua Española",
        "Salida de Español",
        "Inglés",
        "F.I.H.R",
        "Francés",
        "Matemáticas",
        "Ciencias Sociales",
        "Moral y Cívica",
        "Ciencias Naturales",
        "Salida de Ciencias",
        "Educación Artística",
        "Educación Física",
        "Salida",
    ],
    "5": [
        "Lengua Española",
        "Salida de Español",
        "Inglés",
        "F.I.H.R",
        "Francés",
        "Matemáticas",
        "Ciencias Sociales",
        "Moral y Cívica",
        "Ciencias Naturales",
        "Salida de Ciencias",
        "Educación Artística",
        "Educación Física",
        "Salida",
    ],
    "6": [
        "Lengua Española",
        "Salida de Español",
        "Inglés",
        "F.I.H.R",
        "Francés",
        "Matemáticas",
        "Ciencias Sociales",
        "Moral y Cívica",
        "Ciencias Naturales",
        "Salida de Ciencias",
        "Educación Artística",
        "Educación Física",
        "Salida",
    ],
}


def get_or_create_course(Course, course_key):
    aliases = COURSE_ALIASES[course_key]
    for alias in aliases:
        course = Course.objects.filter(name__iexact=alias).first()
        if course:
            return course

    course, _ = Course.objects.get_or_create(
        name=course_key,
        defaults={"active": True},
    )
    return course


def seed_subjects(apps, schema_editor):
    Course = apps.get_model("core", "Course")
    Subject = apps.get_model("core", "Subject")

    for course_key, subject_names in SUBJECTS_BY_COURSE.items():
        course = get_or_create_course(Course, course_key)
        for subject_name in subject_names:
            Subject.objects.get_or_create(
                course=course,
                name=subject_name,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_teacher_responsibles"),
    ]

    operations = [
        migrations.RunPython(seed_subjects, migrations.RunPython.noop),
    ]
