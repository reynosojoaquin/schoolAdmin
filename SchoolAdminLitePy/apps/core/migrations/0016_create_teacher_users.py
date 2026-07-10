import unicodedata

from django.contrib.auth.hashers import make_password
from django.db import migrations


TEMPORARY_PASSWORD = "admin"


def slug_part(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return "".join(ch for ch in ascii_value.lower() if ch.isalnum())


def build_base_username(teacher):
    first_name = (teacher.first_name or "").split()
    last_name = (teacher.last_name or "").split()
    first = slug_part(first_name[0] if first_name else "docente")
    last = slug_part(last_name[0] if last_name else teacher.pk)
    return f"{first}.{last}"


def unique_username(User, base_username, current_user_id=None):
    username = base_username
    counter = 2
    queryset = User.objects.filter(username__iexact=username)
    if current_user_id:
        queryset = queryset.exclude(pk=current_user_id)
    while queryset.exists():
        username = f"{base_username}{counter}"
        counter += 1
        queryset = User.objects.filter(username__iexact=username)
        if current_user_id:
            queryset = queryset.exclude(pk=current_user_id)
    return username


def create_teacher_users(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")
    Teacher = apps.get_model("core", "Teacher")

    docente_group, _ = Group.objects.get_or_create(name="Docente")
    password = make_password(TEMPORARY_PASSWORD)

    for teacher in Teacher.objects.filter(active=True).order_by("last_name", "first_name", "id"):
        base_username = build_base_username(teacher)
        user = teacher.user

        if user is None:
            username = unique_username(User, base_username)
            user = User.objects.create(
                username=username,
                first_name=teacher.first_name,
                last_name=teacher.last_name,
                email=teacher.email,
                password=password,
                is_active=True,
            )
            teacher.user = user
            teacher.save(update_fields=["user", "updated_at"])
        else:
            username = unique_username(User, base_username, current_user_id=user.pk)
            user.username = username
            user.first_name = teacher.first_name
            user.last_name = teacher.last_name
            user.email = teacher.email
            user.password = password
            user.is_active = True
            user.save(update_fields=["username", "first_name", "last_name", "email", "password", "is_active"])

        user.groups.add(docente_group)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_dynamic_roles_and_access_rules"),
    ]

    operations = [
        migrations.RunPython(create_teacher_users, migrations.RunPython.noop),
    ]
