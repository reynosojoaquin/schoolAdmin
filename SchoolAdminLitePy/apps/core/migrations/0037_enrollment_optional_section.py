import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0036_person_gender_choices"),
    ]

    operations = [
        migrations.AlterField(
            model_name="enrollment",
            name="section",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="enrollments",
                to="core.section",
                verbose_name="seccion",
            ),
        ),
    ]
