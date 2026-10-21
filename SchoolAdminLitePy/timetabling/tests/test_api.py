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
from timetabling.services.data_structures import HorarioAsignacion
from timetabling.services.rule_interpreter import interpret_predefined_rules
from timetabling.tasks import _build_assignment_reviews


class GenerarHorarioViewTests(TestCase):
    def test_schedule_assistant_requires_login(self):
        response = self.client.get(reverse("timetabling:asistente_horarios"))

        self.assertEqual(response.status_code, 302)

    def test_schedule_assistant_displays_timetable_navigation(self):
        user = User.objects.create_user(username="assistant-navigation-user")
        self.client.force_login(user)

        response = self.client.get(reverse("timetabling:asistente_horarios"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asistente y reglas")
        self.assertContains(response, 'id="menu-toggle"')
        self.assertContains(response, reverse("timetabling:generar_horario"))
        self.assertNotContains(response, reverse("timetabling:recursos_horario"))

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

    def test_rule_interpreter_recognizes_triple_lesson_patterns(self):
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        course = Course.objects.create(name="Patrones")
        section = Section.objects.create(
            course=course,
            name="A",
            school_year="2026-2027",
        )
        Subject.objects.create(
            section=section,
            name="Ciencias Naturales",
            weekly_hours=6,
        )

        rules = interpret_predefined_rules(
            "Ciencias Naturales debe ir en bloques triples.",
            "2026-2027",
        )

        pattern = next(rule for rule in rules if rule["rule_type"] == "lesson_pattern")
        self.assertEqual(pattern["parameters"]["session_length"], 3)
        self.assertEqual(len(pattern["parameters"]["subject_ids"]), 1)

    def test_rule_interpreter_matches_each_pattern_to_its_subject(self):
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        course = Course.objects.create(name="Patrones")
        section = Section.objects.create(
            course=course,
            name="A",
            school_year="2026-2027",
        )
        double_subject = Subject.objects.create(
            section=section,
            name="Ciencias Naturales",
            weekly_hours=4,
        )
        triple_subject = Subject.objects.create(
            section=section,
            name="Lengua",
            weekly_hours=6,
        )

        rules = interpret_predefined_rules(
            "Ciencias Naturales en bloques dobles y Lengua en bloques triples.",
            "2026-2027",
        )

        patterns = {rule["parameters"]["session_length"]: rule for rule in rules}
        self.assertEqual(patterns[2]["parameters"]["subject_ids"], [double_subject.pk])
        self.assertEqual(patterns[3]["parameters"]["subject_ids"], [triple_subject.pk])

    def test_assignment_review_contains_human_readable_names(self):
        review = _build_assignment_reviews(
            [HorarioAsignacion(1, 10, 100, 1000, 5)],
            {
                "profesores": [{"id": 1, "nombre": "Ana Docente"}],
                "materias": [{"id": 10, "nombre": "Matemáticas"}],
                "grupos": [{"id": 100, "nombre": "Primero A"}],
                "aulas": [{"id": 1000, "nombre": "Aula 1"}],
                "bloques": [{
                    "id": 5,
                    "dia": "LUN",
                    "hora_inicio": "08:00",
                    "hora_fin": "09:00",
                }],
            },
        )

        self.assertEqual(review, [{
            "seccion": "Primero A",
            "asignatura": "Matemáticas",
            "docente": "Ana Docente",
            "aula": "Aula 1",
            "dia": "LUN",
            "hora_inicio": "08:00",
            "hora_fin": "09:00",
        }])

    def test_generator_preflight_sums_teacher_load_across_sections(self):
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        course = Course.objects.create(name="Carga")
        teacher = Teacher.objects.create(first_name="Ana", last_name="Docente")
        for section_name in ("A", "B"):
            section = Section.objects.create(
                course=course,
                name=section_name,
                school_year="2026-2027",
            )
            subject = Subject.objects.create(
                section=section,
                name=f"Asignatura {section_name}",
                weekly_hours=3,
            )
            TeachingAssignment.objects.create(
                section=section,
                subject=subject,
                teacher=teacher,
            )
        Profesor.objects.create(
            docente_administracion=teacher,
            nombre="Ana Docente",
            horas_max_semana=5,
        )
        for day in ("LUN", "MAR", "MIÉ"):
            for order, start in ((1, "08:00"), (2, "09:00")):
                end = "09:00" if order == 1 else "10:00"
                BloqueHorario.objects.create(
                    dia=day,
                    hora_inicio=start,
                    hora_fin=end,
                    orden=order,
                )
        Aula.objects.create(nombre="Aula real", capacidad=30)

        response = self.client.get(reverse("timetabling:generar_horario"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["ready"])
        self.assertEqual(
            response.context["teacher_overloads"][0]["required_hours"],
            6,
        )
        self.assertEqual(
            response.context["teacher_overloads"][0]["maximum_weekly_hours"],
            5,
        )

    def test_get_displays_the_schedule_generator_page(self):
        response = self.client.get(reverse("timetabling:generar_horario"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "timetabling/generar.html")
        self.assertContains(response, "Navegación de horarios")
        self.assertNotContains(response, reverse("timetabling:recursos_horario"))
        self.assertContains(response, "Solicita a un administrador académico")
        self.assertContains(response, "Generación de horarios")
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
        BloqueHorario.objects.create(
            dia="MAR",
            hora_inicio="09:00",
            hora_fin="10:00",
            orden=2,
        )
        confirmed_rule = SchedulingRule.objects.create(
            school_year="2026-2027",
            name="Ana no disponible el lunes",
            rule_type="teacher_unavailable",
            severity=SchedulingRule.HARD,
            status=SchedulingRule.CONFIRMED,
            parameters={"teacher_id": teacher.pk, "days": ["LUN"]},
        )
        Aula.objects.create(nombre="Aula real", capacidad=30)

        response = self.client.post(
            reverse("timetabling:preparar_recursos_horario"),
            data="{}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        linked_group = Grupo.objects.get(seccion_administracion=section)
        linked_group.disponibilidad = {"MAR": [1, 2]}
        linked_group.save(update_fields=["disponibilidad"])
        classroom = Aula.objects.get(nombre="Aula real")
        classroom.disponibilidad = {"MAR": [1, 2]}
        classroom.save(update_fields=["disponibilidad"])

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
        self.assertEqual(datos["grupos"][0]["disponibilidad"], {"MAR": [1, 2]})
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
        self.assertEqual(datos["aulas"][0]["disponibilidad"], {"MAR": [1, 2]})
        self.assertEqual(len(datos["reglas_confirmadas"]), 1)
        self.assertEqual(datos["reglas_confirmadas"][0]["id"], confirmed_rule.pk)
        self.assertEqual(
            datos["reglas_confirmadas"][0]["parameters"]["teacher_id"],
            linked_teacher.pk,
        )

    def test_generation_rejects_daily_capacity_overload(self):
        user = User.objects.create_user(username="overloaded-schedule")
        self.client.force_login(user)
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        course = Course.objects.create(name="Sobrecarga")
        section = Section.objects.create(
            course=course,
            name="A",
            school_year="2026-2027",
        )
        subject = Subject.objects.create(
            section=section,
            name="Matemáticas",
            weekly_hours=3,
        )
        teacher = Teacher.objects.create(first_name="Ana", last_name="Docente")
        TeachingAssignment.objects.create(
            section=section,
            subject=subject,
            teacher=teacher,
        )
        Profesor.objects.create(
            docente_administracion=teacher,
            nombre="Ana Docente",
            disponibilidad={"LUN": [1], "MAR": [1]},
            horas_max_dia=1,
            horas_max_semana=24,
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

        response = self.client.post(
            reverse("timetabling:generar_horario_desde_administracion"),
            data="{}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["sobrecargas_docentes"][0]["required_hours"],
            3,
        )
        self.assertEqual(
            response.json()["sobrecargas_docentes"][0]["available_capacity"],
            2,
        )

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

    def test_teaching_load_report_preview_uses_administration_data(self):
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
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        self.assertContains(response, "Vista previa de carga lectiva")
        self.assertContains(response, "Matemáticas")
        self.assertContains(response, "Ana Docente")
        self.assertContains(response, "Descargar PDF")

    def test_teaching_load_report_download_generates_pdf(self):
        user = User.objects.create_user(username="load-report-pdf")
        self.client.force_login(user)
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        course = Course.objects.create(name="Carga PDF")
        section = Section.objects.create(course=course, name="A", school_year="2026-2027")
        subject = Subject.objects.create(section=section, name="Matemáticas", weekly_hours=5)
        teacher = Teacher.objects.create(first_name="Ana", last_name="Docente")
        TeachingAssignment.objects.create(section=section, subject=subject, teacher=teacher)

        response = self.client.get(reverse("timetabling:descargar_carga_lectiva"))

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
        other_teacher = Teacher.objects.create(first_name="Bruno", last_name="Docente")
        other_section = Section.objects.create(
            course=course,
            name="B",
            school_year="2026-2027",
        )
        other_subject = Subject.objects.create(
            section=other_section,
            name="Lengua",
            weekly_hours=4,
        )
        TeachingAssignment.objects.create(
            section=other_section,
            subject=other_subject,
            teacher=other_teacher,
        )

        preview = self.client.get(
            reverse("timetabling:reporte_carga_lectiva"),
            {"teacher": teacher.pk},
        )
        self.assertContains(preview, "Matemáticas")
        self.assertNotContains(preview, "Lengua")
        self.assertContains(
            preview,
            reverse("timetabling:descargar_carga_lectiva") + f"?teacher={teacher.pk}",
        )

        response = self.client.get(
            reverse("timetabling:descargar_carga_lectiva"),
            {"teacher": teacher.pk},
        )

        self.assertEqual(response.status_code, 200)
        build_pdf.assert_called_once_with("2026-2027", teacher.pk)
        self.assertIn(f"_docente_{teacher.pk}.pdf", response["Content-Disposition"])
