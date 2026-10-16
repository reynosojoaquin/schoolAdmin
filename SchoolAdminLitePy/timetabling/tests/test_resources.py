from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Course, Section, Subject, SystemConfiguration, Teacher
from timetabling.models import (
    Aula,
    AsignacionHorario,
    BloqueHorario,
    Grupo,
    Materia,
    Profesor,
)


class ScheduleResourceViewsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="schedule-admin",
            email="schedule-admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.admin)
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])

    def test_resource_dashboard_shows_configuration_counts(self):
        response = self.client.get(reverse("timetabling:recursos_horario"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recursos de horarios")
        self.assertContains(response, "No hay bloques configurados")
        self.assertContains(response, "No hay aulas configuradas")

    def test_resource_dashboard_is_restricted_to_academic_managers(self):
        user = User.objects.create_user(username="teacher-user")
        self.client.force_login(user)

        response = self.client.get(reverse("timetabling:recursos_horario"))

        self.assertEqual(response.status_code, 403)

    def test_unassigned_subject_links_to_a_prefilled_teacher_assignment_form(self):
        course = Course.objects.create(name="Primero")
        section = Section.objects.create(
            course=course,
            name="A",
            school_year="2026-2027",
        )
        subject = Subject.objects.create(
            section=section,
            name="Matemáticas",
            weekly_hours=5,
        )

        response = self.client.get(reverse("timetabling:recursos_horario"))

        self.assertContains(response, "Asignaturas que necesitan docente")
        self.assertContains(
            response,
            f"?section={section.pk}&amp;subject={subject.pk}",
        )
        form_response = self.client.get(
            reverse("core:teaching_assignment_create"),
            {"section": section.pk, "subject": subject.pk},
        )

        self.assertEqual(form_response.status_code, 200)
        self.assertEqual(form_response.context["form"].initial["section"], str(section.pk))
        self.assertEqual(form_response.context["form"].initial["subject"], str(subject.pk))

    def test_creating_room_saves_day_availability(self):
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

        response = self.client.post(
            reverse("timetabling:aula_create"),
            {
                "nombre": "Laboratorio 1",
                "tipo": "laboratorio",
                "capacidad": 28,
                "activa": "on",
                "limitar_LUN": "on",
                "bloques_LUN": ["1"],
            },
        )

        room = Aula.objects.get(nombre="Laboratorio 1")
        self.assertRedirects(response, reverse("timetabling:recursos_horario"))
        self.assertEqual(
            room.disponibilidad,
            {"LUN": [1], "MAR": [1], "MIÉ": [], "JUE": [], "VIE": []},
        )

    def test_block_form_rejects_overlapping_times(self):
        BloqueHorario.objects.create(
            dia="LUN",
            hora_inicio="08:00",
            hora_fin="09:00",
            orden=1,
        )

        response = self.client.post(
            reverse("timetabling:bloque_horario_create"),
            {
                "dia": "LUN",
                "orden": 2,
                "hora_inicio": "08:30",
                "hora_fin": "09:30",
                "activo": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "se superpone")
        self.assertEqual(BloqueHorario.objects.count(), 1)

    def test_teacher_profile_updates_availability_and_hour_limits(self):
        teacher = Teacher.objects.create(first_name="Ana", last_name="Docente")
        profile = Profesor.objects.create(
            docente_administracion=teacher,
            nombre="Ana Docente",
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

        form_response = self.client.get(
            reverse("timetabling:profesor_horario_update", args=[profile.pk]),
        )
        self.assertContains(form_response, 'class="field field-choice-group"')

        response = self.client.post(
            reverse("timetabling:profesor_horario_update", args=[profile.pk]),
            {
                "horas_max_dia": 5,
                "horas_max_semana": 22,
                "limitar_LUN": "on",
                "bloques_LUN": ["1"],
            },
        )

        profile.refresh_from_db()
        self.assertRedirects(response, reverse("timetabling:recursos_horario"))
        self.assertEqual(profile.horas_max_dia, 5)
        self.assertEqual(profile.horas_max_semana, 22)
        self.assertEqual(
            profile.disponibilidad,
            {"LUN": [1], "MAR": [1], "MIÉ": [], "JUE": [], "VIE": []},
        )

    def test_section_profile_updates_availability(self):
        course = Course.objects.create(name="Primero")
        section = Section.objects.create(
            course=course,
            name="A",
            school_year="2026-2027",
        )
        profile = Grupo.objects.create(
            seccion_administracion=section,
            nombre="A",
            grado="Primero",
            disponibilidad={"MAR": [1]},
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
        form_response = self.client.get(
            reverse("timetabling:grupo_horario_update", args=[profile.pk]),
        )
        self.assertTrue(form_response.context["form"]["limitar_LUN"].value())
        self.assertEqual(form_response.context["form"]["bloques_LUN"].value(), [])
        self.assertFalse(form_response.context["form"]["limitar_MAR"].value())

        response = self.client.post(
            reverse("timetabling:grupo_horario_update", args=[profile.pk]),
            {
                "limitar_LUN": "on",
                "bloques_LUN": ["1"],
            },
        )

        profile.refresh_from_db()
        self.assertRedirects(response, reverse("timetabling:recursos_horario"))
        self.assertEqual(
            profile.disponibilidad,
            {"LUN": [1], "MAR": [1], "MIÉ": [], "JUE": [], "VIE": []},
        )

    def test_schedule_resources_in_use_cannot_be_deleted(self):
        teacher = Teacher.objects.create(first_name="Ana", last_name="Docente")
        course = Course.objects.create(name="Primero")
        section = Section.objects.create(
            course=course,
            name="A",
            school_year="2026-2027",
        )
        subject = Subject.objects.create(
            section=section,
            name="Matemáticas",
            weekly_hours=1,
        )
        profile = Profesor.objects.create(
            docente_administracion=teacher,
            nombre="Ana Docente",
        )
        timetable_subject = Materia.objects.create(
            asignatura_administracion=subject,
            nombre=subject.name,
            horas_semanales_requeridas=1,
        )
        group = Grupo.objects.create(
            seccion_administracion=section,
            nombre="A",
            grado="Primero",
        )
        room = Aula.objects.create(nombre="Aula 1", capacidad=30)
        block = BloqueHorario.objects.create(
            dia="LUN",
            hora_inicio="08:00",
            hora_fin="09:00",
            orden=1,
        )
        assignment = AsignacionHorario.objects.create(
            profesor=profile,
            materia=timetable_subject,
            grupo=group,
            aula=room,
            bloque=block,
        )

        response = self.client.post(
            reverse("timetabling:aula_delete", args=[room.pk]),
        )

        self.assertRedirects(response, reverse("timetabling:recursos_horario"))
        self.assertTrue(Aula.objects.filter(pk=room.pk).exists())
        self.assertTrue(AsignacionHorario.objects.filter(pk=assignment.pk).exists())

    def test_preparing_resources_reports_missing_master_data(self):
        response = self.client.post(
            reverse("timetabling:preparar_recursos_horario_ui"),
        )

        self.assertRedirects(response, reverse("timetabling:recursos_horario"))
        self.assertContains(
            self.client.get(reverse("timetabling:recursos_horario")),
            "No hay secciones activas",
        )
