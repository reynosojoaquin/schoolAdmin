from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0042_common_nationality_locations"),
    ]

    operations = [
        migrations.AddField(
            model_name="grade",
            name="recovery_1",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="recuperacion p1-p2"),
        ),
        migrations.AddField(
            model_name="grade",
            name="recovery_2",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="recuperacion p3-p4"),
        ),
    ]
