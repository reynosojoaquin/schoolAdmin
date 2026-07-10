from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_attendance"),
    ]

    operations = [
        migrations.AlterField(
            model_name="administrativeemployee",
            name="photo_url",
            field=models.FileField(blank=True, upload_to="people/photos/", verbose_name="foto"),
        ),
        migrations.AlterField(
            model_name="student",
            name="photo_url",
            field=models.FileField(blank=True, upload_to="people/photos/", verbose_name="foto"),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="photo_url",
            field=models.FileField(blank=True, upload_to="people/photos/", verbose_name="foto"),
        ),
    ]
