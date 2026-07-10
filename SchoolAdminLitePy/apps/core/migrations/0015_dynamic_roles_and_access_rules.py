import django.db.models.deletion
from django.db import migrations, models


ACCESS_PERMISSIONS = [
    ("manage_users_roles", "Puede gestionar usuarios y roles"),
    ("manage_people", "Puede gestionar estudiantes, docentes y personal"),
    ("manage_academic_setup", "Puede gestionar cursos, secciones, asignaturas y docencia"),
    ("view_all_academic", "Puede ver todas las secciones y calificaciones"),
    ("view_own_sections", "Puede ver sus secciones asignadas"),
    ("edit_grades", "Puede editar calificaciones"),
    ("import_grades", "Puede importar calificaciones desde Excel"),
    ("view_grade_stats", "Puede ver estadisticas de calificaciones"),
]


ROLE_PERMISSIONS = {
    "Administrador": [code for code, _ in ACCESS_PERMISSIONS],
    "Coordinador academico": [
        "manage_academic_setup",
        "view_all_academic",
        "edit_grades",
        "import_grades",
        "view_grade_stats",
    ],
    "Coordinador de registro": [
        "manage_people",
        "view_all_academic",
        "view_grade_stats",
    ],
    "Digitacion": [
        "manage_people",
        "view_all_academic",
        "edit_grades",
        "import_grades",
    ],
    "Docente": [
        "view_own_sections",
        "edit_grades",
        "import_grades",
        "view_grade_stats",
    ],
    "Consulta": [
        "view_all_academic",
        "view_grade_stats",
    ],
}


def seed_access_roles(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")

    content_type, _ = ContentType.objects.get_or_create(
        app_label="core",
        model="accessrule",
    )

    permissions = {}
    for codename, name in ACCESS_PERMISSIONS:
        permission, _ = Permission.objects.get_or_create(
            content_type=content_type,
            codename=codename,
            defaults={"name": name},
        )
        permissions[codename] = permission

    for role_name, codenames in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        for codename in codenames:
            group.permissions.add(permissions[codename])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0014_teacher_user_and_roles"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="nombre")),
            ],
            options={
                "verbose_name": "regla de acceso",
                "verbose_name_plural": "reglas de acceso",
                "permissions": [
                    ("manage_users_roles", "Puede gestionar usuarios y roles"),
                    ("manage_people", "Puede gestionar estudiantes, docentes y personal"),
                    ("manage_academic_setup", "Puede gestionar cursos, secciones, asignaturas y docencia"),
                    ("view_all_academic", "Puede ver todas las secciones y calificaciones"),
                    ("view_own_sections", "Puede ver sus secciones asignadas"),
                    ("edit_grades", "Puede editar calificaciones"),
                    ("import_grades", "Puede importar calificaciones desde Excel"),
                    ("view_grade_stats", "Puede ver estadisticas de calificaciones"),
                ],
            },
        ),
        migrations.RunPython(seed_access_roles, migrations.RunPython.noop),
    ]
