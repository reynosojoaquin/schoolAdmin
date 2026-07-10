import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="nombre")),
                ("active", models.BooleanField(default=True, verbose_name="activo")),
            ],
            options={
                "verbose_name": "curso",
                "verbose_name_plural": "cursos",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Province",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="nombre")),
            ],
            options={
                "verbose_name": "provincia",
                "verbose_name_plural": "provincias",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("first_name", models.CharField(max_length=120, verbose_name="nombres")),
                ("last_name", models.CharField(max_length=120, verbose_name="apellidos")),
                ("document_id", models.CharField(blank=True, max_length=20, verbose_name="cedula")),
                ("birth_date", models.DateField(blank=True, null=True, verbose_name="fecha de nacimiento")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="correo")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="telefono")),
                ("address", models.CharField(blank=True, max_length=240, verbose_name="direccion")),
                ("active", models.BooleanField(default=True, verbose_name="activo")),
            ],
            options={
                "verbose_name": "estudiante",
                "verbose_name_plural": "estudiantes",
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="City",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120, verbose_name="nombre")),
                (
                    "province",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cities",
                        to="core.province",
                        verbose_name="provincia",
                    ),
                ),
            ],
            options={
                "verbose_name": "ciudad",
                "verbose_name_plural": "ciudades",
                "ordering": ["province__name", "name"],
                "unique_together": {("province", "name")},
            },
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("school_year", models.CharField(max_length=20, verbose_name="ano escolar")),
                ("active", models.BooleanField(default=True, verbose_name="activa")),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="enrollments",
                        to="core.course",
                        verbose_name="curso",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="core.student",
                        verbose_name="estudiante",
                    ),
                ),
            ],
            options={
                "verbose_name": "inscripcion",
                "verbose_name_plural": "inscripciones",
                "ordering": ["-school_year", "course__name", "student__last_name"],
                "unique_together": {("student", "course", "school_year")},
            },
        ),
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120, verbose_name="nombre")),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="subjects",
                        to="core.course",
                        verbose_name="curso",
                    ),
                ),
            ],
            options={
                "verbose_name": "asignatura",
                "verbose_name_plural": "asignaturas",
                "ordering": ["course__name", "name"],
                "unique_together": {("course", "name")},
            },
        ),
        migrations.CreateModel(
            name="Sector",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120, verbose_name="nombre")),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sectors",
                        to="core.city",
                        verbose_name="ciudad",
                    ),
                ),
            ],
            options={
                "verbose_name": "sector",
                "verbose_name_plural": "sectores",
                "ordering": ["city__name", "name"],
                "unique_together": {("city", "name")},
            },
        ),
        migrations.AddField(
            model_name="student",
            name="sector",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="students",
                to="core.sector",
                verbose_name="sector",
            ),
        ),
        migrations.CreateModel(
            name="Grade",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period_1", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="p1")),
                ("period_2", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="p2")),
                ("period_3", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="p3")),
                ("period_4", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="p4")),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grades",
                        to="core.enrollment",
                        verbose_name="inscripcion",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="grades",
                        to="core.subject",
                        verbose_name="asignatura",
                    ),
                ),
            ],
            options={
                "verbose_name": "calificacion",
                "verbose_name_plural": "calificaciones",
                "ordering": ["enrollment", "subject__name"],
                "unique_together": {("enrollment", "subject")},
            },
        ),
    ]

