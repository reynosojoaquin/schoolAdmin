from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.core.models import (
    Course,
    Section,
    Subject,
    SystemConfiguration,
    Teacher,
    TeachingAssignment,
)
from timetabling.models import Aula, BloqueHorario, Grupo, Materia, Profesor


class GenerarHorarioViewTests(TestCase):
    def test_get_displays_the_schedule_generator_page(self):
        response = self.client.get(reverse("timetabling:generar_horario"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "timetabling/generar.html")
        self.assertContains(response, "Horarios de secciones")
        self.assertContains(response, "No se crean datos de ejemplo")
        self.assertNotContains(response, "Cargar ejemplo")

    def test_post_keeps_the_json_generation_endpoint(self):
        user = User.objects.create_user(username="schedule-test")
        self.client.force_login(user)
        response = self.client.post(
            reverse("timetabling:generar_horario"),
            data="{}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("bloques", response.json())

    def test_generation_uses_current_administration_sections_and_assignments(self):
        user = User.objects.create_user(username="schedule-admin")
        self.client.force_login(user)
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        course = Course.objects.create(name="Primero")
        section = Section.objects.create(
            course=course,
            name="A",
            school_year="2026-2027",
        )
        subject = Subject.objects.create(
            section=section,
            name="Matemáticas",
            weekly_hours=2,
        )
        teacher = Teacher.objects.create(first_name="Ana", last_name="Docente")
        TeachingAssignment.objects.create(
            section=section,
            subject=subject,
            teacher=teacher,
        )
        BloqueHorario.objects.create(
            dia="LUN",
            hora_inicio="08:00",
            hora_fin="09:00",
            orden=1,
        )
        BloqueHorario.objects.create(
            dia="MAR",
            hora_inicio="08:00",
            hora_fin="09:00",
            orden=1,
        )
        Aula.objects.create(nombre="Aula real", capacidad=30)

        with patch("timetabling.tasks.ejecutar_generacion.delay") as enqueue:
            response = self.client.post(
                reverse("timetabling:generar_horario_desde_administracion"),
                data="{}",
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 202)
        datos = enqueue.call_args.args[1]
        linked_group = Grupo.objects.get(seccion_administracion=section)
        linked_subject = Materia.objects.get(asignatura_administracion=subject)
        linked_teacher = Profesor.objects.get(docente_administracion=teacher)
        self.assertEqual(datos["grupos"][0]["id"], linked_group.pk)
        self.assertEqual(datos["grupos"][0]["nombre"], "Primero A")
        self.assertEqual(
            datos["grupos"][0]["materias_asignadas"],
            [{
                "materia_id": linked_subject.pk,
                "horas_asignadas": 2,
                "profesor_id": linked_teacher.pk,
            }],
        )
        self.assertEqual(datos["profesores"][0]["nombre"], "Ana Docente")
        self.assertEqual(datos["aulas"][0]["nombre"], "Aula real")

    def test_generation_requires_sections_to_have_assigned_teachers(self):
        user = User.objects.create_user(username="schedule-validation")
        self.client.force_login(user)
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        course = Course.objects.create(name="Segundo")
        section = Section.objects.create(
            course=course,
            name="B",
            school_year="2026-2027",
        )
        Subject.objects.create(section=section, name="Lengua", weekly_hours=3)

        response = self.client.post(
            reverse("timetabling:generar_horario_desde_administracion"),
            data="{}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Asignaciones docentes", response.json()["error"])

    def test_teaching_load_report_uses_administration_data(self):
        user = User.objects.create_user(username="load-report")
        self.client.force_login(user)
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        course = Course.objects.create(name="Carga 2")
        section = Section.objects.create(course=course, name="A", school_year="2026-2027")
        subject = Subject.objects.create(section=section, name="Matemáticas", weekly_hours=5)
        teacher = Teacher.objects.create(first_name="Ana", last_name="Docente")
        TeachingAssignment.objects.create(section=section, subject=subject, teacher=teacher)

        response = self.client.get(reverse("timetabling:reporte_carga_lectiva"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("carga_lectiva_2026-2027.pdf", response["Content-Disposition"])
        self.assertGreater(len(response.content), 1000)
