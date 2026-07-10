from django.db import migrations, models


SCHOOL_YEAR = "2025-2026"

SECTIONS_BY_COURSE = {
    "1": ["A", "B", "C", "D"],
    "2": ["A", "B"],
    "3": ["A", "B"],
    "4": ["A", "B"],
    "5": ["A", "B"],
    "6": ["A", "B"],
}

CURRICULUM = {
    "1A": {
        "Lengua Española": 6,
        "Taller de lectoescritura": 1,
        "Inglés": 4,
        "F.I.H.R": 2,
        "Francés": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Educación Artística": 2,
        "Taller de Artes-BEM": 1,
        "Educación Física": 2,
        "Taller juegos de mesa": 1,
        "Taller de Deporte": 1,
    },
    "1B": {
        "Lengua Española": 6,
        "Taller de lectoescritura": 1,
        "Inglés": 4,
        "Francés": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "F.I.H.R": 2,
        "Educación Artística": 2,
        "Taller de Artes-BEM": 1,
        "Educación Física": 2,
        "Taller juegos de mesa": 1,
        "Taller de Deporte": 1,
    },
    "1C": {
        "Lengua Española": 6,
        "Taller de lectoescritura": 1,
        "F.I.H.R": 2,
        "Inglés": 4,
        "Francés": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Educación Artística": 2,
        "Taller de Artes-BEM": 1,
        "Educación Física": 2,
        "Taller juegos de mesa": 1,
        "Taller de Deporte": 1,
    },
    "1D": {
        "Lengua Española": 6,
        "Taller de lectoescritura": 1,
        "F.I.H.R": 2,
        "Inglés": 4,
        "Francés": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Educación Artística": 2,
        "Taller de Artes-BEM": 1,
        "Educación Física": 2,
        "Taller juegos de mesa": 1,
        "Taller de Deporte": 1,
    },
    "2A": {
        "Lengua Española": 6,
        "F.I.H.R": 2,
        "Taller de lectoescritura": 1,
        "Inglés": 4,
        "Francés": 2,
        "Taller de Francés": 1,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Educación Artística": 2,
        "Taller de Artes-BEM": 1,
        "Educación Física": 2,
        "Taller de Deporte": 1,
    },
    "2B": {
        "Lengua Española": 6,
        "F.I.H.R": 2,
        "Taller de lectoescritura": 1,
        "Inglés": 4,
        "Francés": 2,
        "Taller de Francés": 1,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Educación Artística": 2,
        "Taller de Artes-BEM": 1,
        "Educación Física": 2,
        "Taller de Deporte": 1,
    },
    "3A": {
        "Lengua Española": 6,
        "Inglés": 4,
        "Francés": 2,
        "Taller de Francés": 1,
        "Matemáticas": 7,
        "F.I.H.R": 2,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Educación Artística": 2,
        "Educación Física": 2,
        "Taller juegos de mesa": 1,
        "Taller de Deporte": 2,
    },
    "3B": {
        "Lengua Española": 6,
        "Inglés": 4,
        "Francés": 2,
        "Taller de Francés": 1,
        "Matemáticas": 7,
        "F.I.H.R": 2,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Educación Artística": 2,
        "Educación Física": 2,
        "Taller juegos de mesa": 1,
        "Taller de Deporte": 2,
    },
    "4A": {
        "Lengua Española": 6,
        "Salida de Español": 2,
        "Inglés": 4,
        "F.I.H.R": 2,
        "Francés": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Salida de Ciencias": 2,
        "Educación Artística": 2,
        "Educación Física": 2,
    },
    "4B": {
        "Lengua Española": 6,
        "Inglés": 4,
        "F.I.H.R": 2,
        "Francés": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Salida": 4,
        "Educación Artística": 2,
        "Educación Física": 2,
    },
    "5A": {
        "Lengua Española": 6,
        "Salida de Español": 2,
        "Inglés": 4,
        "Francés": 2,
        "F.I.H.R": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Salida de Ciencias": 2,
        "Educación Artística": 2,
        "Educación Física": 2,
    },
    "5B": {
        "Lengua Española": 6,
        "Inglés": 4,
        "Francés": 2,
        "F.I.H.R": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Salida": 4,
        "Educación Artística": 2,
        "Educación Física": 2,
    },
    "6A": {
        "Lengua Española": 6,
        "Salida de Español": 2,
        "Inglés": 4,
        "Francés": 2,
        "F.I.H.R": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Salida de Ciencias": 2,
        "Educación Artística": 2,
        "Educación Física": 2,
    },
    "6B": {
        "Lengua Española": 6,
        "Inglés": 4,
        "Francés": 2,
        "F.I.H.R": 2,
        "Matemáticas": 7,
        "Ciencias Sociales": 4,
        "Moral y Cívica": 1,
        "Ciencias Naturales": 6,
        "Salida": 4,
        "Educación Artística": 2,
        "Educación Física": 2,
    },
}


def sync_carga_horaria(apps, schema_editor):
    Course = apps.get_model("core", "Course")
    Section = apps.get_model("core", "Section")
    Subject = apps.get_model("core", "Subject")

    for course_name, section_names in SECTIONS_BY_COURSE.items():
        course, _ = Course.objects.get_or_create(name=course_name, defaults={"active": True})
        if not course.active:
            course.active = True
            course.save(update_fields=["active"])

        for section_name in section_names:
            section, _ = Section.objects.get_or_create(
                course=course,
                name=section_name,
                school_year=SCHOOL_YEAR,
                defaults={"active": True},
            )
            if not section.active:
                section.active = True
                section.save(update_fields=["active"])

            section_key = f"{course_name}{section_name}"
            for subject_name, weekly_hours in CURRICULUM[section_key].items():
                subject, created = Subject.objects.get_or_create(
                    section=section,
                    name=subject_name,
                    defaults={"weekly_hours": weekly_hours},
                )
                if not created and subject.weekly_hours != weekly_hours:
                    subject.weekly_hours = weekly_hours
                    subject.save(update_fields=["weekly_hours"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0019_section_scoped_subjects"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="weekly_hours",
            field=models.PositiveSmallIntegerField(default=0, verbose_name="horas semanales"),
        ),
        migrations.RunPython(sync_carga_horaria, migrations.RunPython.noop),
    ]
