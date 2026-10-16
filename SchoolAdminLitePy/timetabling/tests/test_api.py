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
from timetabling.models import (
    AssistantConversation,
    AssistantMemory,
    AssistantMessage,
    Aula,
    BloqueHorario,
    Grupo,
    Materia,
    Profesor,
    SchedulingRule,
)


class GenerarHorarioViewTests(TestCase):
    def test_schedule_assistant_requires_login(self):
        response = self.client.get(reverse("timetabling:asistente_horarios"))

        self.assertEqual(response.status_code, 302)

    @patch(
        "timetabling.api.views.request_local_assistant",
        return_value={"available": True, "content": "Regla interpretada.", "model": "local-test"},
    )
    def test_schedule_assistant_persists_conversation_and_confirmed_memory(self, local_assistant):
        user = User.objects.create_user(username="assistant-user")
        self.client.force_login(user)
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])

        response = self.client.post(
            reverse("timetabling:asistente_horarios"),
            {
                "prompt": "Ramón no debe impartir clases los viernes.",
                "remember": "on",
                "memory_title": "Disponibilidad de Ramón",
            },
        )

        conversation = AssistantConversation.objects.get(user=user)
        self.assertRedirects(
            response,
            f"{reverse('timetabling:asistente_horarios')}?conversation={conversation.pk}",
        )
        self.assertEqual(conversation.messages.count(), 2)
        self.assertTrue(conversation.messages.filter(role=AssistantMessage.USER).exists())
        self.assertTrue(conversation.messages.filter(role=AssistantMessage.ASSISTANT).exists())
        memory = AssistantMemory.objects.get(created_by=user)
        self.assertEqual(memory.school_year, "2026-2027")
        self.assertEqual(memory.status, AssistantMemory.CONFIRMED)
        self.assertEqual(memory.revisions.count(), 1)
        local_assistant.assert_called_once_with(
            "Ramón no debe impartir clases los viernes.",
            "2026-2027",
        )

    @patch(
        "timetabling.api.views.request_local_assistant",
        return_value={"available": False, "content": "Modelo pendiente."},
    )
    def test_schedule_assistant_proposes_and_confirms_predefined_rules(self, local_assistant):
        user = User.objects.create_user(username="rule-user")
        self.client.force_login(user)
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        teacher = Teacher.objects.create(first_name="Zeferino", last_name="Único")
        course = Course.objects.create(name="Reglas")
        section = Section.objects.create(course=course, name="A", school_year="2026-2027")
        Subject.objects.create(section=section, name="Ciencias Naturales", weekly_hours=6)

        response = self.client.post(
            reverse("timetabling:asistente_horarios"),
            {
                "prompt": (
                    "Zeferino Único no puede trabajar los viernes. Ciencias Naturales "
                    "debe ir en bloques dobles y quiero minimizar los huecos."
                ),
            },
        )

        self.assertEqual(response.status_code, 302)
        rules = SchedulingRule.objects.filter(created_by=user)
        self.assertEqual(rules.count(), 3)
        unavailable = rules.get(rule_type="teacher_unavailable")
        self.assertEqual(unavailable.parameters["teacher_id"], teacher.pk)
        self.assertEqual(unavailable.parameters["days"], ["VIE"])

        response = self.client.post(
            reverse("timetabling:confirmar_regla_asistente", args=[unavailable.pk]),
            {"action": "confirm"},
        )

        self.assertEqual(response.status_code, 302)
        unavailable.refresh_from_db()
        self.assertEqual(unavailable.status, SchedulingRule.CONFIRMED)
        memory = AssistantMemory.objects.get(structured_data__rule_id=unavailable.pk)
        self.assertEqual(memory.structured_data["rule_type"], "teacher_unavailable")
        self.assertEqual(memory.status, AssistantMemory.CONFIRMED)

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

    def test_teacher_filter_shows_only_assigned_sections(self):
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        course = Course.objects.create(name="Filtro")
        section_a = Section.objects.create(course=course, name="A", school_year="2026-2027")
        section_b = Section.objects.create(course=course, name="B", school_year="2026-2027")
        subject_a = Subject.objects.create(section=section_a, name="Matemáticas", weekly_hours=5)
        subject_b = Subject.objects.create(section=section_b, name="Lengua", weekly_hours=4)
        teacher_a = Teacher.objects.create(first_name="Ana", last_name="Álvarez")
        teacher_b = Teacher.objects.create(first_name="Bruno", last_name="Báez")
        TeachingAssignment.objects.create(section=section_a, subject=subject_a, teacher=teacher_a)
        TeachingAssignment.objects.create(section=section_b, subject=subject_b, teacher=teacher_b)

        response = self.client.get(
            reverse("timetabling:generar_horario"),
            {"teacher": teacher_a.pk},
        )

        self.assertContains(response, "Docente seleccionado:")
        self.assertContains(response, "Filtro A")
        self.assertNotContains(response, "Filtro B")
        self.assertContains(response, f"?teacher={teacher_a.pk}")

    @patch("timetabling.api.views.build_teaching_load_pdf", return_value=b"%PDF-filtered")
    def test_teaching_load_report_filters_by_teacher(self, build_pdf):
        user = User.objects.create_user(username="filtered-load-report")
        self.client.force_login(user)
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        teacher = Teacher.objects.create(first_name="Ana", last_name="Docente")
        course = Course.objects.create(name="Carga filtrada")
        section = Section.objects.create(course=course, name="A", school_year="2026-2027")
        subject = Subject.objects.create(section=section, name="Matemáticas", weekly_hours=5)
        TeachingAssignment.objects.create(section=section, subject=subject, teacher=teacher)

        response = self.client.get(
            reverse("timetabling:reporte_carga_lectiva"),
            {"teacher": teacher.pk},
        )

        self.assertEqual(response.status_code, 200)
        build_pdf.assert_called_once_with("2026-2027", teacher.pk)
        self.assertIn(f"_docente_{teacher.pk}.pdf", response["Content-Disposition"])
