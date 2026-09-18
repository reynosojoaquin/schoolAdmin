import django.db.models.deletion
from django.db import migrations, models


COMMON_LOCATIONS = {
    "Haitiana": {
        "Ouest": ["Port-au-Prince", "Pétion-Ville"],
        "Nord": ["Cap-Haïtien"],
    },
    "Estadounidense": {
        "New York": ["New York City"],
        "Florida": ["Miami", "Orlando"],
    },
    "Canadiense": {
        "Ontario": ["Toronto", "Ottawa"],
        "Québec": ["Montréal"],
    },
    "Mexicana": {
        "Ciudad de México": ["Ciudad de México"],
        "Jalisco": ["Guadalajara"],
    },
    "Cubana": {
        "La Habana": ["La Habana"],
        "Santiago de Cuba": ["Santiago de Cuba"],
    },
    "Puertorriqueña": {
        "San Juan": ["San Juan"],
        "Ponce": ["Ponce"],
    },
    "Jamaiquina": {
        "Kingston": ["Kingston"],
        "Saint Catherine": ["Spanish Town"],
    },
    "Venezolana": {
        "Distrito Capital": ["Caracas"],
        "Zulia": ["Maracaibo"],
    },
    "Colombiana": {
        "Bogotá D.C.": ["Bogotá"],
        "Antioquia": ["Medellín"],
    },
    "Ecuatoriana": {
        "Pichincha": ["Quito"],
        "Guayas": ["Guayaquil"],
    },
    "Peruana": {
        "Lima": ["Lima"],
        "Arequipa": ["Arequipa"],
    },
    "Boliviana": {
        "La Paz": ["La Paz"],
        "Santa Cruz": ["Santa Cruz de la Sierra"],
    },
    "Chilena": {
        "Región Metropolitana de Santiago": ["Santiago"],
        "Valparaíso": ["Valparaíso"],
    },
    "Argentina": {
        "Buenos Aires": ["La Plata", "Mar del Plata"],
        "Córdoba": ["Córdoba"],
    },
    "Brasileña": {
        "São Paulo": ["São Paulo"],
        "Rio de Janeiro": ["Rio de Janeiro"],
    },
    "Uruguaya": {
        "Montevideo": ["Montevideo"],
        "Canelones": ["Canelones"],
    },
    "Paraguaya": {
        "Asunción": ["Asunción"],
        "Central": ["San Lorenzo"],
    },
    "Española": {
        "Comunidad de Madrid": ["Madrid"],
        "Cataluña": ["Barcelona"],
    },
    "Francesa": {
        "Île-de-France": ["París"],
        "Auvergne-Rhône-Alpes": ["Lyon"],
    },
    "Italiana": {
        "Lazio": ["Roma"],
        "Lombardia": ["Milán"],
    },
    "Alemana": {
        "Berlín": ["Berlín"],
        "Baviera": ["Múnich"],
    },
    "Británica": {
        "Gran Londres": ["Londres"],
        "Midlands Occidentales": ["Birmingham"],
    },
    "China": {
        "Pekín": ["Pekín"],
        "Shanghái": ["Shanghái"],
    },
    "Japonesa": {
        "Tokio": ["Tokio"],
        "Osaka": ["Osaka"],
    },
}


def seed_locations(apps, schema_editor):
    Nationality = apps.get_model("core", "Nationality")
    Province = apps.get_model("core", "Province")
    City = apps.get_model("core", "City")
    database = schema_editor.connection.alias

    dominicana, _ = Nationality.objects.using(database).get_or_create(name="Dominicana")
    Province.objects.using(database).filter(nationality__isnull=True).update(nationality=dominicana)

    for nationality_name, provinces in COMMON_LOCATIONS.items():
        nationality, _ = Nationality.objects.using(database).get_or_create(name=nationality_name)
        for province_name, city_names in provinces.items():
            province, _ = Province.objects.using(database).get_or_create(
                nationality=nationality,
                name=province_name,
            )
            for city_name in city_names:
                City.objects.using(database).get_or_create(province=province, name=city_name)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0041_nationality_provinces"),
    ]

    operations = [
        migrations.RunPython(seed_locations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="province",
            name="nationality",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="provinces",
                to="core.nationality",
                verbose_name="nacionalidad",
            ),
        ),
    ]
