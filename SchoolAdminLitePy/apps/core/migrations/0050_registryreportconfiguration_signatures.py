from django.core.validators import FileExtensionValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0049_subject_include_in_registry_reports"),
    ]

    operations = [
        migrations.AddField(
            model_name="registryreportconfiguration",
            name="teacher_signature",
            field=models.FileField(
                blank=True,
                upload_to="registry_reports/signatures/",
                validators=[FileExtensionValidator(["png", "jpg", "jpeg", "webp"])],
                verbose_name="firma del maestro encargado",
            ),
        ),
        migrations.AddField(
            model_name="registryreportconfiguration",
            name="director_signature",
            field=models.FileField(
                blank=True,
                upload_to="registry_reports/signatures/",
                validators=[FileExtensionValidator(["png", "jpg", "jpeg", "webp"])],
                verbose_name="firma del director",
            ),
        ),
    ]
