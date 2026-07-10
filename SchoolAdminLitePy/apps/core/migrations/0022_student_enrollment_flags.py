from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_remove_general_sections"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="new_admission",
            field=models.BooleanField(default=False, verbose_name="nuevo ingreso"),
        ),
        migrations.AddField(
            model_name="student",
            name="promoted",
            field=models.BooleanField(default=False, verbose_name="promovido"),
        ),
    ]
