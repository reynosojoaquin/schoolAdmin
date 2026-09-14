from django.db import migrations, models
import django.db.models.deletion


PROVINCES_AND_CITIES = {
    "Distrito Nacional": ["Santo Domingo de Guzmán"],
    "Azua": ["Azua", "Estebanía", "Guayabal", "Las Charcas", "Las Yayas de Viajama", "Padre Las Casas", "Peralta", "Pueblo Viejo", "Sabana Yegua", "Tábara Arriba"],
    "Baoruco": ["Neiba", "Galván", "Los Ríos", "Tamayo", "Villa Jaragua"],
    "Barahona": ["Barahona", "Cabral", "El Peñón", "Enriquillo", "Fundación", "Jaquimeyes", "La Ciénaga", "Las Salinas", "Paraíso", "Polo", "Vicente Noble"],
    "Dajabón": ["Dajabón", "El Pino", "Loma de Cabrera", "Partido", "Restauración"],
    "Duarte": ["San Francisco de Macorís", "Arenoso", "Castillo", "Eugenio María de Hostos", "Las Guáranas", "Pimentel", "Villa Riva"],
    "Elías Piña": ["Comendador", "Bánica", "El Llano", "Hondo Valle", "Juan Santiago", "Pedro Santana"],
    "El Seibo": ["Santa Cruz de El Seibo", "Miches"],
    "Espaillat": ["Moca", "Cayetano Germosén", "Gaspar Hernández", "Jamao al Norte", "San Víctor"],
    "Independencia": ["Jimaní", "Cristóbal", "Duvergé", "La Descubierta", "Mella", "Postrer Río"],
    "La Altagracia": ["Salvaleón de Higüey", "San Rafael del Yuma"],
    "La Romana": ["La Romana", "Guaymate", "Villa Hermosa"],
    "La Vega": ["Concepción de La Vega", "Constanza", "Jarabacoa", "Jima Abajo"],
    "María Trinidad Sánchez": ["Nagua", "Cabrera", "El Factor", "Río San Juan"],
    "Monte Cristi": ["San Fernando de Monte Cristi", "Castañuelas", "Guayubín", "Las Matas de Santa Cruz", "Pepillo Salcedo", "Villa Vásquez"],
    "Pedernales": ["Pedernales", "Oviedo"],
    "Peravia": ["Baní", "Nizao", "Matanzas"],
    "Puerto Plata": ["San Felipe de Puerto Plata", "Altamira", "Guananico", "Imbert", "Los Hidalgos", "Luperón", "Sosúa", "Villa Isabela", "Villa Montellano"],
    "Hermanas Mirabal": ["Salcedo", "Tenares", "Villa Tapia"],
    "Samaná": ["Santa Bárbara de Samaná", "Las Terrenas", "Sánchez"],
    "San Cristóbal": ["San Cristóbal", "Bajos de Haina", "Cambita Garabitos", "Los Cacaos", "Sabana Grande de Palenque", "San Gregorio de Nigua", "Villa Altagracia", "Yaguate"],
    "San Juan": ["San Juan de la Maguana", "Bohechío", "El Cercado", "Juan de Herrera", "Las Matas de Farfán", "Vallejuelo"],
    "San Pedro de Macorís": ["San Pedro de Macorís", "Consuelo", "Guayacanes", "Los Llanos", "Quisqueya", "Ramón Santana"],
    "Sánchez Ramírez": ["Cotuí", "Cevicos", "Fantino", "La Mata"],
    "Santiago": ["Santiago de los Caballeros", "Bisonó", "Jánico", "Licey al Medio", "Puñal", "Sabana Iglesia", "San José de las Matas", "Tamboril", "Villa González", "Baitoa"],
    "Santiago Rodríguez": ["San Ignacio de Sabaneta", "Los Almácigos", "Monción"],
    "Valverde": ["Santa Cruz de Mao", "Esperanza", "Laguna Salada"],
    "Monseñor Nouel": ["Bonao", "Maimón", "Piedra Blanca"],
    "Monte Plata": ["Monte Plata", "Bayaguana", "Peralvillo", "Sabana Grande de Boyá", "Yamasá"],
    "Hato Mayor": ["Hato Mayor del Rey", "El Valle", "Sabana de la Mar"],
    "San José de Ocoa": ["San José de Ocoa", "Rancho Arriba", "Sabana Larga"],
    "Santo Domingo": ["Santo Domingo Este", "Boca Chica", "Los Alcarrizos", "Pedro Brand", "San Antonio de Guerra", "Santo Domingo Norte", "Santo Domingo Oeste"],
}

NATIONALITIES = [
    "Dominicana", "Haitiana", "Estadounidense", "Canadiense", "Mexicana",
    "Cubana", "Puertorriqueña", "Jamaiquina", "Venezolana", "Colombiana",
    "Ecuatoriana", "Peruana", "Boliviana", "Chilena", "Argentina", "Brasileña",
    "Uruguaya", "Paraguaya", "Española", "Francesa", "Italiana", "Alemana",
    "Británica", "China", "Japonesa", "Otra",
]

EMPLOYEE_TYPES_AND_POSITIONS = {
    "Administrativo": [
        "Director/a administrativo/a", "Secretario/a", "Auxiliar administrativo/a",
        "Encargado/a de registro", "Digitador/a", "Contador/a", "Tesorero/a",
        "Recepcionista",
    ],
    "Apoyo institucional": [
        "Bibliotecario/a", "Encargado/a TIC", "Soporte técnico", "Enfermero/a",
        "Orientador/a", "Psicólogo/a",
    ],
    "Servicios generales": [
        "Conserje", "Portero/a", "Jardinero/a", "Cocinero/a", "Ayudante de cocina",
        "Chofer", "Mensajero/a",
    ],
    "Seguridad": ["Vigilante", "Sereno/a"],
    "Técnico y mantenimiento": [
        "Técnico/a informático/a", "Técnico/a de mantenimiento", "Electricista",
        "Plomero/a",
    ],
}


def seed_reference_catalogs(apps, schema_editor):
    Province = apps.get_model("core", "Province")
    City = apps.get_model("core", "City")
    Nationality = apps.get_model("core", "Nationality")
    EmployeeType = apps.get_model("core", "EmployeeType")
    EmployeePosition = apps.get_model("core", "EmployeePosition")

    for province_name, city_names in PROVINCES_AND_CITIES.items():
        province, _ = Province.objects.get_or_create(name=province_name)
        for city_name in city_names:
            City.objects.get_or_create(province=province, name=city_name)

    for nationality_name in NATIONALITIES:
        Nationality.objects.get_or_create(name=nationality_name)

    for type_name, position_names in EMPLOYEE_TYPES_AND_POSITIONS.items():
        employee_type, _ = EmployeeType.objects.get_or_create(name=type_name)
        for position_name in position_names:
            EmployeePosition.objects.get_or_create(
                employee_type=employee_type,
                name=position_name,
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0034_systemconfiguration")]

    operations = [
        migrations.AddField(
            model_name="administrativeemployee",
            name="birth_province",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_birth_province_people", to="core.province", verbose_name="provincia de nacimiento"),
        ),
        migrations.AddField(
            model_name="student",
            name="birth_province",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_birth_province_people", to="core.province", verbose_name="provincia de nacimiento"),
        ),
        migrations.AddField(
            model_name="teacher",
            name="birth_province",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_birth_province_people", to="core.province", verbose_name="provincia de nacimiento"),
        ),
        migrations.AlterField(
            model_name="administrativeemployee",
            name="birthplace",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_people", to="core.city", verbose_name="ciudad de nacimiento"),
        ),
        migrations.AlterField(
            model_name="student",
            name="birthplace",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_people", to="core.city", verbose_name="ciudad de nacimiento"),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="birthplace",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s_people", to="core.city", verbose_name="ciudad de nacimiento"),
        ),
        migrations.AlterField(
            model_name="administrativeemployee",
            name="marital_status",
            field=models.CharField(blank=True, choices=[("Soltero/a", "Soltero/a"), ("Casado/a", "Casado/a"), ("Union libre", "Unión libre"), ("Divorciado/a", "Divorciado/a"), ("Viudo/a", "Viudo/a"), ("Separado/a", "Separado/a")], max_length=60, verbose_name="estado civil"),
        ),
        migrations.AlterField(
            model_name="student",
            name="marital_status",
            field=models.CharField(blank=True, choices=[("Soltero/a", "Soltero/a"), ("Casado/a", "Casado/a"), ("Union libre", "Unión libre"), ("Divorciado/a", "Divorciado/a"), ("Viudo/a", "Viudo/a"), ("Separado/a", "Separado/a")], max_length=60, verbose_name="estado civil"),
        ),
        migrations.AlterField(
            model_name="teacher",
            name="marital_status",
            field=models.CharField(blank=True, choices=[("Soltero/a", "Soltero/a"), ("Casado/a", "Casado/a"), ("Union libre", "Unión libre"), ("Divorciado/a", "Divorciado/a"), ("Viudo/a", "Viudo/a"), ("Separado/a", "Separado/a")], max_length=60, verbose_name="estado civil"),
        ),
        migrations.RunPython(seed_reference_catalogs, migrations.RunPython.noop),
    ]
