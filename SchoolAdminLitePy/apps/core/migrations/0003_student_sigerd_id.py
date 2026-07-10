from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_dotnet_school_structure"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="sigerd_id",
            field=models.CharField(blank=True, max_length=40, verbose_name="codigo SIGERD"),
        ),
        migrations.AddIndex(
            model_name="student",
            index=models.Index(fields=["document_id"], name="core_student_doc_idx"),
        ),
        migrations.AddIndex(
            model_name="student",
            index=models.Index(fields=["sigerd_id"], name="core_student_sigerd_idx"),
        ),
    ]
