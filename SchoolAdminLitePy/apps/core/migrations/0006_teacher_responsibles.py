import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_teaching_assignments"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="responsible",
        ),
        migrations.RemoveField(
            model_name="subject",
            name="responsible",
        ),
        migrations.AddField(
            model_name="course",
            name="responsible",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="responsible_courses",
                to="core.teacher",
                verbose_name="docente responsable",
            ),
        ),
        migrations.AddField(
            model_name="subject",
            name="responsible",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="responsible_subjects",
                to="core.teacher",
                verbose_name="docente responsable",
            ),
        ),
    ]
