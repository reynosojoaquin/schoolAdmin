from django.db import migrations


TEACHERS = [
    ("Luisa Mar\u00eda", "Caraballo P\u00e9rez", "06000189313"),
    ("Jos\u00e9 Mart\u00edn", "Hilario Fco.", "056-0119460-7"),
    ("Alexandra", "Gonz\u00e1lez Tolentino", "048-0105319-2"),
    ("Milly", "Peralta Santos", "056-0127712-1"),
    ("Marcos Antonio", "Peralta S\u00e1nchez", "056-0059493-0"),
    ("Joaquin M.", "Reynoso", "056-0109834-5"),
    ("Mar\u00eda Teresa", "Polanco Castro", "056-0118019-2"),
    ("Yanna Mar\u00eda", "Paulino P\u00e9rez", "402-2607563-4"),
    ("Carmen Inmaculada", "Cruz Mota", "056-0053769-9"),
    ("Juana Mar\u00eda", "Then Then", "056-0123552-5"),
    ("Isabel D\u00edsla", "Santana", "056-0129650-1"),
    ("Ruth Esther", "Tineo De la Cruz", "056-0156791-9"),
    ("Ram\u00f3n Aurelio", "G\u00f3mez Bel\u00e9n", "155-0001923-5"),
    ("Madelyn", "Ortiz Compres", "402-2801339-3"),
    ("Olkania Maridelis", "De la Cruz Caraballo", "402-1353848-7"),
    ("Francisca", "Espinal Marte", "056-00925-44-9"),
    ("Yelenny", "Fern\u00e1ndez N\u00fa\u00f1ez", "402-3745578-3"),
    ("Marianela", "Liberato Reyes", "056-0131405-6"),
    ("William A.", "Candelario Bautista", "056-0006940-4"),
    ("Escarlett", "Paulino Moya", "056-0088329-1"),
    ("Roselis Anyeline", "Santana Tejada", "402-2247195-1"),
    ("Darlenny", "N\u00fa\u00f1ez Cordones", "402-2514887-9"),
    ("Nathanael", "Holgu\u00edn Castillo", "056-0160142-9"),
    ("Reymond Joel", "Eusebio Laureano", "056-0168333-6"),
    ("Lisbeth", "Alvarado Taberas", "402-2559380-1"),
    ("Isabel", "Esca\u00f1o Alm\u00e1nzar", "056-0002204-9"),
    ("Pablo Rafael", "Mart\u00ednez P\u00e9rez", "056-0133341-1"),
    ("Juan Carlos", "Santos Santos", "402-2400314-1"),
    ("Carla Michel", "Gonz\u00e1lez Abad", "001-1823797-3"),
    ("Lucy Nathali", "Silva Almonte", "402-1566212-9"),
    ("Mercedes", "Marte De L\u00f3pez", "056-0137300-3"),
    ("Felix Ramon", "Escol\u00e1stico Hidalgo", "056-0154573-3"),
]


def normalize_document(value):
    return "".join(ch for ch in (value or "") if ch.isdigit())


def find_existing_teacher(Teacher, first_name, last_name, document_id):
    normalized_document = normalize_document(document_id)
    for teacher in Teacher.objects.all():
        if normalize_document(teacher.document_id) == normalized_document:
            return teacher

    return Teacher.objects.filter(
        first_name__iexact=first_name,
        last_name__iexact=last_name,
    ).first()


def seed_teachers(apps, schema_editor):
    Teacher = apps.get_model("core", "Teacher")

    for first_name, last_name, document_id in TEACHERS:
        teacher = find_existing_teacher(Teacher, first_name, last_name, document_id)
        if teacher:
            teacher.first_name = first_name
            teacher.last_name = last_name
            teacher.document_id = document_id
            teacher.active = True
            teacher.save(update_fields=["first_name", "last_name", "document_id", "active", "updated_at"])
            continue

        Teacher.objects.create(
            first_name=first_name,
            last_name=last_name,
            document_id=document_id,
            active=True,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_sync_subjects_with_existing_sections"),
    ]

    operations = [
        migrations.RunPython(seed_teachers, migrations.RunPython.noop),
    ]
