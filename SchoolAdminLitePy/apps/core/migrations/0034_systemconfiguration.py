from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0033_guidancefollowup_evidence_file"),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemConfiguration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("institution_name", models.CharField(default="Liceo Secundario Coronel Rafael T. Fernandez Dominguez", max_length=180, verbose_name="nombre del centro")),
                ("logo", models.FileField(blank=True, upload_to="branding/", validators=[django.core.validators.FileExtensionValidator(["png", "jpg", "jpeg", "webp"])], verbose_name="logo institucional")),
            ],
            options={
                "verbose_name": "configuracion del sistema",
                "verbose_name_plural": "configuracion del sistema",
            },
        ),
    ]
