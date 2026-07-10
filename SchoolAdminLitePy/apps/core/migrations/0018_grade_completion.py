from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_competency_grade_matrix"),
    ]

    operations = [
        migrations.CreateModel(
            name="GradeCompletion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("cf", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="cf")),
                ("cf_50", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="50% cf")),
                ("cef", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="cef")),
                ("cef_50", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="50% cef")),
                ("ccf", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="ccf")),
                ("ccf_30", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="30% ccf")),
                ("ceex", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="ceex")),
                ("ceex_70", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="70% ceex")),
                ("cexf", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="cexf")),
                ("special_cf", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="cf especial")),
                ("special_ce", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name="ce especial")),
                ("approved", models.CharField(blank=True, max_length=1, verbose_name="aprobado")),
                ("reproved", models.CharField(blank=True, max_length=1, verbose_name="reprobado")),
                ("enrollment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="grade_completions", to="core.enrollment", verbose_name="inscripcion")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="grade_completions", to="core.subject", verbose_name="asignatura")),
            ],
            options={
                "verbose_name": "evaluacion completiva",
                "verbose_name_plural": "evaluaciones completivas",
                "ordering": ["enrollment", "subject__name"],
                "unique_together": {("enrollment", "subject")},
            },
        ),
    ]
