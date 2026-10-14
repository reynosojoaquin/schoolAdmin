from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0050_registryreportconfiguration_signatures"),
    ]

    operations = [
        migrations.AddField(
            model_name="enrollment",
            name="list_order",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="orden manual de lista",
            ),
        ),
    ]
