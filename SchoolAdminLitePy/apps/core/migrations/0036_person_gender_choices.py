from django.db import migrations, models


GENDER_CHOICES = [("Masculino", "Masculino"), ("Femenino", "Femenino")]


class Migration(migrations.Migration):
    dependencies = [("core", "0035_employee_reference_catalogs")]

    operations = [
        migrations.AlterField(
            model_name="administrativeemployee",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=GENDER_CHOICES,
                max_length=20,
                verbose_name="sexo",
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=GENDER_CHOICES,
                max_length=20,
                verbose_name="sexo",
            ),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=GENDER_CHOICES,
                max_length=20,
                verbose_name="sexo",
            ),
        ),
    ]
