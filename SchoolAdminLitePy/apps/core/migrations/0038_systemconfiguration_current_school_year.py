from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0037_enrollment_optional_section"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfiguration",
            name="current_school_year",
            field=models.CharField(default="2026-2027", max_length=20, verbose_name="ano escolar actual"),
        ),
    ]
