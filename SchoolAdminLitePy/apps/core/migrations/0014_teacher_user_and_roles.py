import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


ROLE_NAMES = ["Administrador", "Docente", "Consulta"]


def create_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in ROLE_NAMES:
        Group.objects.get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0013_assign_subjects_to_sections"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="teacher_profile",
                to=settings.AUTH_USER_MODEL,
                verbose_name="usuario del sistema",
            ),
        ),
        migrations.RunPython(create_roles, migrations.RunPython.noop),
    ]
