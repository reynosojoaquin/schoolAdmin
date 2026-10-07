from django.db import migrations, models


def migrate_pair_recoveries(apps, schema_editor):
    Grade = apps.get_model("core", "Grade")
    for grade in Grade.objects.all().iterator():
        pair_1 = grade.recovery_pair_1
        pair_2 = grade.recovery_pair_2
        if pair_1 is not None:
            if grade.period_2 is not None and (grade.period_1 is None or grade.period_2 < grade.period_1):
                grade.recovery_2 = pair_1
            else:
                grade.recovery_1 = pair_1
        if pair_2 is not None:
            if grade.period_4 is not None and (grade.period_3 is None or grade.period_4 < grade.period_3):
                grade.recovery_4 = pair_2
            else:
                grade.recovery_3 = pair_2
        grade.save(update_fields=["recovery_1", "recovery_2", "recovery_3", "recovery_4"])


class Migration(migrations.Migration):
    dependencies = [("core", "0043_grade_recoveries")]

    operations = [
        migrations.RenameField(model_name="grade", old_name="recovery_1", new_name="recovery_pair_1"),
        migrations.RenameField(model_name="grade", old_name="recovery_2", new_name="recovery_pair_2"),
        migrations.AddField(model_name="grade", name="recovery_1", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="recuperacion p1")),
        migrations.AddField(model_name="grade", name="recovery_2", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="recuperacion p2")),
        migrations.AddField(model_name="grade", name="recovery_3", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="recuperacion p3")),
        migrations.AddField(model_name="grade", name="recovery_4", field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="recuperacion p4")),
        migrations.RunPython(migrate_pair_recoveries, migrations.RunPython.noop),
        migrations.RemoveField(model_name="grade", name="recovery_pair_1"),
        migrations.RemoveField(model_name="grade", name="recovery_pair_2"),
    ]
