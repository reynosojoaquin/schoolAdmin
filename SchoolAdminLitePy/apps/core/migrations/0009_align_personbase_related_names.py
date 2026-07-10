import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_align_enrollment_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="administrativeemployee",
            name="birthplace",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_people",
                to="core.birthplace",
                verbose_name="lugar de nacimiento",
            ),
        ),
        migrations.AlterField(
            model_name="administrativeemployee",
            name="nationality",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_people",
                to="core.nationality",
                verbose_name="nacionalidad",
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="birthplace",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_people",
                to="core.birthplace",
                verbose_name="lugar de nacimiento",
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="nationality",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_people",
                to="core.nationality",
                verbose_name="nacionalidad",
            ),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="birthplace",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_people",
                to="core.birthplace",
                verbose_name="lugar de nacimiento",
            ),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="nationality",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_people",
                to="core.nationality",
                verbose_name="nacionalidad",
            ),
        ),
    ]
