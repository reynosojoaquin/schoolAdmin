from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0051_enrollment_list_order"),
        ("timetabling", "0003_alter_horariojob_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profesor",
            name="docente_administracion",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="perfil_horario",
                to="core.teacher",
                verbose_name="docente de administracion",
            ),
        ),
        migrations.AddField(
            model_name="materia",
            name="asignatura_administracion",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="materia_horario",
                to="core.subject",
                verbose_name="asignatura de administracion",
            ),
        ),
        migrations.AddField(
            model_name="grupo",
            name="seccion_administracion",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="grupo_horario",
                to="core.section",
                verbose_name="seccion de administracion",
            ),
        ),
    ]
