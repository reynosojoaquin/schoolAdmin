import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import AdministrativeEmployeeForm
from .models import AdministrativeEmployee, City, Course, EmployeePosition, EmployeeType, Enrollment, Province, Section, Student, SystemConfiguration


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class SystemConfigurationTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_login_displays_default_logo_and_session_label(self):
        response = self.client.get(reverse("core:login"))

        self.assertContains(response, "logo-centro-default")
        self.assertContains(response, "Iniciar sesi&oacute;n", html=True)

    def test_only_system_managers_can_update_branding(self):
        regular_user = User.objects.create_user("regular", password="test-password")
        self.client.force_login(regular_user)
        self.assertEqual(self.client.get(reverse("core:system_configuration")).status_code, 403)

        admin = User.objects.create_superuser("admin", "admin@example.com", "test-password")
        self.client.force_login(admin)
        response = self.client.post(
            reverse("core:system_configuration"),
            {
                "institution_name": "Centro Educativo de Prueba",
                "logo": SimpleUploadedFile("logo.png", b"fake-png-content", content_type="image/png"),
            },
        )

        self.assertRedirects(response, reverse("core:system_configuration"))
        configuration = SystemConfiguration.objects.get(pk=1)
        self.assertEqual(configuration.institution_name, "Centro Educativo de Prueba")
        self.assertTrue(configuration.logo.name.startswith("branding/logo"))

    def test_authenticated_layout_uses_configured_logo(self):
        admin = User.objects.create_superuser("admin", "admin@example.com", "test-password")
        SystemConfiguration.objects.create(
            logo=SimpleUploadedFile("custom-logo.jpg", b"fake-jpg-content", content_type="image/jpeg")
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("core:dashboard"))

        self.assertContains(response, "/media/branding/custom-logo.jpg")
        self.assertContains(response, reverse("core:system_configuration"))


class AdministrativeEmployeeCatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("catalog-admin", "admin@example.com", "password")
        cls.province = Province.objects.create(name="Provincia de prueba")
        cls.other_province = Province.objects.create(name="Otra provincia de prueba")
        cls.city = City.objects.create(province=cls.province, name="Ciudad de prueba")
        cls.other_city = City.objects.create(province=cls.other_province, name="Otra ciudad")
        cls.employee_type = EmployeeType.objects.create(name="Tipo de prueba")
        cls.other_employee_type = EmployeeType.objects.create(name="Otro tipo de prueba")
        cls.position = EmployeePosition.objects.create(
            employee_type=cls.employee_type,
            name="Posición de prueba",
        )
        cls.other_position = EmployeePosition.objects.create(
            employee_type=cls.other_employee_type,
            name="Otra posición",
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_city_endpoint_filters_by_province(self):
        response = self.client.get(
            reverse("core:birth_cities_options"),
            {"province": self.province.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["cities"], [{"id": self.city.pk, "text": self.city.name}])

    def test_position_endpoint_filters_by_employee_type(self):
        response = self.client.get(
            reverse("core:employee_positions_options"),
            {"employee_type": self.employee_type.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["positions"],
            [{"id": self.position.pk, "text": self.position.name}],
        )

    def test_form_limits_dependent_catalogs(self):
        form = AdministrativeEmployeeForm(
            data={
                "birth_province": self.province.pk,
                "employee_type": self.employee_type.pk,
            }
        )

        self.assertQuerySetEqual(form.fields["birthplace"].queryset, [self.city])
        self.assertQuerySetEqual(form.fields["position"].queryset, [self.position])

    def test_gender_is_a_select_with_expected_options(self):
        form = AdministrativeEmployeeForm()

        self.assertEqual(
            list(form.fields["gender"].choices),
            [("", "---------"), ("Masculino", "Masculino"), ("Femenino", "Femenino")],
        )

    def test_employee_phone_is_saved_and_can_be_updated(self):
        response = self.client.post(reverse("core:employee_create"), {
            "first_name": "Ana", "last_name": "Perez", "phone": "809-555-0101",
        })
        self.assertEqual(response.status_code, 302)
        employee = AdministrativeEmployee.objects.get(first_name="Ana")
        self.assertEqual(employee.phones.get().number, "809-555-0101")
        response = self.client.post(reverse("core:employee_update", args=[employee.pk]), {
            "first_name": "Ana", "last_name": "Perez", "phone": "809-555-0102",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(employee.phones.get().number, "809-555-0102")


    def test_form_rejects_city_or_position_from_another_parent(self):
        form = AdministrativeEmployeeForm(
            data={
                "first_name": "Ana",
                "last_name": "Pérez",
                "birth_province": self.province.pk,
                "birthplace": self.other_city.pk,
                "employee_type": self.employee_type.pk,
                "position": self.other_position.pk,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("birthplace", form.errors)
        self.assertIn("position", form.errors)


class SectionEnrollmentTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_superuser("enrollment-admin", "admin@example.com", "password"))
        self.course = Course.objects.create(name="Curso pruebas inscripcion")
        self.section = Section.objects.create(course=self.course, name="A", school_year="2026-2027")
        configuration = SystemConfiguration.get_solo()
        configuration.current_school_year = "2026-2027"
        configuration.save(update_fields=["current_school_year"])
        self.student = Student.objects.create(first_name="Eva", last_name="Perez", new_admission=True)

    def test_enrollment_is_assigned_to_selected_section(self):
        response = self.client.post(reverse("core:section_enrollment", args=[self.section.pk]), {
            "students": [self.student.pk],
        })
        self.assertRedirects(response, reverse("core:section_students", args=[self.section.pk]))
        enrollment = Enrollment.objects.get(student=self.student)
        self.assertEqual(enrollment.section, self.section)
        self.student.refresh_from_db()
        self.assertFalse(self.student.new_admission)
