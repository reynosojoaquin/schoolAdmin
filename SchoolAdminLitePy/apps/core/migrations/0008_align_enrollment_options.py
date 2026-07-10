from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_seed_subjects_from_carga_horaria"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="enrollment",
            options={
                "ordering": ["-school_year", "course__name", "section__name", "student__last_name"],
                "verbose_name": "inscripcion",
                "verbose_name_plural": "inscripciones",
            },
        ),
    ]
