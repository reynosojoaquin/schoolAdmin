from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Province(TimeStampedModel):
    name = models.CharField("nombre", max_length=120, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "provincia"
        verbose_name_plural = "provincias"

    def __str__(self):
        return self.name


class City(TimeStampedModel):
    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name="cities",
        verbose_name="provincia",
    )
    name = models.CharField("nombre", max_length=120)

    class Meta:
        ordering = ["province__name", "name"]
        unique_together = [("province", "name")]
        verbose_name = "ciudad"
        verbose_name_plural = "ciudades"

    def __str__(self):
        return f"{self.name}, {self.province}"


class Sector(TimeStampedModel):
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="sectors",
        verbose_name="ciudad",
    )
    name = models.CharField("nombre", max_length=120)

    class Meta:
        ordering = ["city__name", "name"]
        unique_together = [("city", "name")]
        verbose_name = "sector"
        verbose_name_plural = "sectores"

    def __str__(self):
        return f"{self.name}, {self.city.name}"


class Nationality(TimeStampedModel):
    name = models.CharField("nombre", max_length=120, unique=True)
    legacy_id = models.IntegerField("id anterior", null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "nacionalidad"
        verbose_name_plural = "nacionalidades"

    def __str__(self):
        return self.name


class Birthplace(TimeStampedModel):
    name = models.CharField("nombre", max_length=120, unique=True)
    legacy_id = models.IntegerField("id anterior", null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "lugar de nacimiento"
        verbose_name_plural = "lugares de nacimiento"

    def __str__(self):
        return self.name


class PersonBase(TimeStampedModel):
    first_name = models.CharField("nombres", max_length=120)
    last_name = models.CharField("apellidos", max_length=120)
    document_id = models.CharField("cedula", max_length=20, blank=True)
    active = models.BooleanField("activo", default=True)
    email = models.EmailField("correo", blank=True)
    gender = models.CharField("sexo", max_length=20, blank=True)
    photo_url = models.CharField("url de foto", max_length=300, blank=True)
    nationality = models.ForeignKey(
        Nationality,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_people",
        verbose_name="nacionalidad",
    )
    marital_status = models.CharField("estado civil", max_length=60, blank=True)
    license_number = models.CharField("licencia", max_length=80, blank=True)
    birthplace = models.ForeignKey(
        Birthplace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_people",
        verbose_name="lugar de nacimiento",
    )
    birth_date = models.DateField("fecha de nacimiento", null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class AddressType(TimeStampedModel):
    description = models.CharField("descripcion", max_length=120, unique=True)

    class Meta:
        ordering = ["description"]
        verbose_name = "tipo de direccion"
        verbose_name_plural = "tipos de direccion"

    def __str__(self):
        return self.description


class PhoneType(TimeStampedModel):
    description = models.CharField("descripcion", max_length=120, unique=True)

    class Meta:
        ordering = ["description"]
        verbose_name = "tipo de telefono"
        verbose_name_plural = "tipos de telefono"

    def __str__(self):
        return self.description


class ContactType(TimeStampedModel):
    description = models.CharField("descripcion", max_length=120, unique=True)

    class Meta:
        ordering = ["description"]
        verbose_name = "tipo de contacto"
        verbose_name_plural = "tipos de contacto"

    def __str__(self):
        return self.description


class AccessRule(TimeStampedModel):
    name = models.CharField("nombre", max_length=120, unique=True)

    class Meta:
        permissions = [
            ("manage_users_roles", "Puede gestionar usuarios y roles"),
            ("manage_people", "Puede gestionar estudiantes, docentes y personal"),
            ("manage_academic_setup", "Puede gestionar cursos, secciones, asignaturas y docencia"),
            ("view_all_academic", "Puede ver todas las secciones y calificaciones"),
            ("view_own_sections", "Puede ver sus secciones asignadas"),
            ("edit_grades", "Puede editar calificaciones"),
            ("import_grades", "Puede importar calificaciones desde Excel"),
            ("view_grade_stats", "Puede ver estadisticas de calificaciones"),
        ]
        verbose_name = "regla de acceso"
        verbose_name_plural = "reglas de acceso"

    def __str__(self):
        return self.name


class Course(TimeStampedModel):
    name = models.CharField("nombre", max_length=120, unique=True)
    responsible = models.ForeignKey(
        "Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_courses",
        verbose_name="docente responsable",
    )
    active = models.BooleanField("activo", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "curso"
        verbose_name_plural = "cursos"

    def __str__(self):
        return self.name

    @property
    def active_sections_count(self):
        return self.sections.filter(active=True).count()

    @property
    def active_students_count(self):
        return self.enrollments.filter(active=True).count()


class Section(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="curso",
    )
    name = models.CharField("seccion", max_length=20)
    school_year = models.CharField("ano escolar", max_length=20, blank=True)
    responsible = models.ForeignKey(
        "Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sections",
        verbose_name="docente guia",
    )
    active = models.BooleanField("activa", default=True)

    class Meta:
        ordering = ["course__name", "name", "-school_year"]
        unique_together = [("course", "name", "school_year")]
        verbose_name = "seccion"
        verbose_name_plural = "secciones"

    def __str__(self):
        label = f"{self.course}{self.name}"
        return f"{label} ({self.school_year})" if self.school_year else label

    @property
    def active_students_count(self):
        return self.enrollments.filter(active=True).count()

    @property
    def active_assignments_count(self):
        return self.teaching_assignments.filter(active=True).count()


class Subject(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="subjects",
        verbose_name="curso",
    )
    name = models.CharField("nombre", max_length=120)
    responsible = models.ForeignKey(
        "Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_subjects",
        verbose_name="docente responsable",
    )

    class Meta:
        ordering = ["course__name", "name"]
        unique_together = [("course", "name")]
        verbose_name = "asignatura"
        verbose_name_plural = "asignaturas"

    def __str__(self):
        return f"{self.name} - {self.course}"

    @property
    def active_assignments_count(self):
        return self.teaching_assignments.filter(active=True).count()


class TeachingAssignment(TimeStampedModel):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="teaching_assignments",
        verbose_name="seccion",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teaching_assignments",
        verbose_name="asignatura",
    )
    teacher = models.ForeignKey(
        "Teacher",
        on_delete=models.PROTECT,
        related_name="teaching_assignments",
        verbose_name="docente",
    )
    active = models.BooleanField("activa", default=True)

    class Meta:
        ordering = ["section__course__name", "section__name", "subject__name"]
        unique_together = [("section", "subject")]
        verbose_name = "asignacion docente"
        verbose_name_plural = "asignaciones docentes"

    def __str__(self):
        return f"{self.section} - {self.subject.name} - {self.teacher}"

    def clean(self):
        if self.section_id and self.subject_id and self.section.course_id != self.subject.course_id:
            raise ValidationError("La asignatura debe pertenecer al mismo curso de la seccion.")


class Student(PersonBase):
    sigerd_id = models.CharField("codigo SIGERD", max_length=40, blank=True)
    phone = models.CharField("telefono", max_length=30, blank=True)
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="sector",
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["document_id"], name="core_student_doc_idx"),
            models.Index(fields=["sigerd_id"], name="core_student_sigerd_idx"),
        ]
        verbose_name = "estudiante"
        verbose_name_plural = "estudiantes"


class Teacher(PersonBase):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_profile",
        verbose_name="usuario del sistema",
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "docente"
        verbose_name_plural = "docentes"


class EmployeeType(TimeStampedModel):
    name = models.CharField("nombre", max_length=120, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "tipo de empleado"
        verbose_name_plural = "tipos de empleado"

    def __str__(self):
        return self.name


class EmployeePosition(TimeStampedModel):
    employee_type = models.ForeignKey(
        EmployeeType,
        on_delete=models.PROTECT,
        related_name="positions",
        verbose_name="tipo de empleado",
    )
    name = models.CharField("nombre", max_length=120)

    class Meta:
        ordering = ["employee_type__name", "name"]
        unique_together = [("employee_type", "name")]
        verbose_name = "posicion de empleado"
        verbose_name_plural = "posiciones de empleados"

    def __str__(self):
        return f"{self.name} - {self.employee_type}"


class AdministrativeEmployee(PersonBase):
    employee_type = models.ForeignKey(
        EmployeeType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="administrative_employees",
        verbose_name="tipo de empleado",
    )
    position = models.ForeignKey(
        EmployeePosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="administrative_employees",
        verbose_name="posicion",
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "empleado administrativo"
        verbose_name_plural = "empleados administrativos"


class Address(TimeStampedModel):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="addresses",
        verbose_name="estudiante",
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="addresses",
        verbose_name="docente",
    )
    administrative_employee = models.ForeignKey(
        AdministrativeEmployee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="addresses",
        verbose_name="empleado administrativo",
    )
    address_type = models.ForeignKey(
        AddressType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="addresses",
        verbose_name="tipo",
    )
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name="addresses")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name="addresses")
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True, related_name="addresses")
    street = models.CharField("calle", max_length=180)
    number = models.CharField("numero", max_length=40)
    apartment = models.CharField("apartamento", max_length=60, blank=True)
    longitude = models.CharField("longitud", max_length=80, blank=True)
    latitude = models.CharField("latitud", max_length=80, blank=True)

    class Meta:
        ordering = ["street", "number"]
        verbose_name = "direccion"
        verbose_name_plural = "direcciones"

    def __str__(self):
        return f"{self.street} {self.number}".strip()


class Phone(TimeStampedModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name="phones")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name="phones")
    administrative_employee = models.ForeignKey(
        AdministrativeEmployee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="phones",
    )
    phone_type = models.ForeignKey(PhoneType, on_delete=models.SET_NULL, null=True, blank=True, related_name="phones")
    number = models.CharField("numero", max_length=40)

    class Meta:
        ordering = ["number"]
        verbose_name = "telefono"
        verbose_name_plural = "telefonos"

    def __str__(self):
        return self.number


class Contact(TimeStampedModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name="contacts")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name="contacts")
    first_name = models.CharField("nombre", max_length=120)
    last_name = models.CharField("apellido", max_length=120)
    phone = models.CharField("telefono", max_length=40)
    address = models.CharField("direccion", max_length=240, blank=True)
    contact_type = models.ForeignKey(
        ContactType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts",
        verbose_name="tipo",
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "contacto"
        verbose_name_plural = "contactos"

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class Competency(TimeStampedModel):
    description = models.CharField("descripcion", max_length=240, unique=True)

    class Meta:
        ordering = ["description"]
        verbose_name = "competencia"
        verbose_name_plural = "competencias"

    def __str__(self):
        return self.description


class SubjectCompetency(TimeStampedModel):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="subject_competencies")
    competency = models.ForeignKey(Competency, on_delete=models.PROTECT, related_name="subject_competencies")

    class Meta:
        ordering = ["subject__name", "competency__description"]
        unique_together = [("subject", "competency")]
        verbose_name = "competencia por asignatura"
        verbose_name_plural = "competencias por asignatura"

    def __str__(self):
        return f"{self.subject} - {self.competency}"


class Enrollment(TimeStampedModel):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="estudiante",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="enrollments",
        verbose_name="curso",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
        verbose_name="seccion",
    )
    school_year = models.CharField("ano escolar", max_length=20)
    active = models.BooleanField("activa", default=True)

    class Meta:
        ordering = ["-school_year", "course__name", "section__name", "student__last_name"]
        unique_together = [("student", "course", "school_year")]
        verbose_name = "inscripcion"
        verbose_name_plural = "inscripciones"

    def __str__(self):
        section = f" {self.section.name}" if self.section else ""
        return f"{self.student} - {self.course}{section} ({self.school_year})"


class Grade(TimeStampedModel):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="inscripcion",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="grades",
        verbose_name="asignatura",
    )
    subject_competency = models.ForeignKey(
        SubjectCompetency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grades",
        verbose_name="competencia",
    )
    period_1 = models.DecimalField("p1", max_digits=5, decimal_places=2, null=True, blank=True)
    period_2 = models.DecimalField("p2", max_digits=5, decimal_places=2, null=True, blank=True)
    period_3 = models.DecimalField("p3", max_digits=5, decimal_places=2, null=True, blank=True)
    period_4 = models.DecimalField("p4", max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["enrollment", "subject__name"]
        unique_together = [("enrollment", "subject", "subject_competency")]
        verbose_name = "calificacion"
        verbose_name_plural = "calificaciones"

    @property
    def average(self):
        values = [self.period_1, self.period_2, self.period_3, self.period_4]
        valid_values = [value for value in values if value is not None]
        if not valid_values:
            return None
        return sum(valid_values) / len(valid_values)

    def __str__(self):
        return f"{self.enrollment.student} - {self.subject}"


class GradeCompletion(TimeStampedModel):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="grade_completions",
        verbose_name="inscripcion",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="grade_completions",
        verbose_name="asignatura",
    )
    cf = models.DecimalField("cf", max_digits=5, decimal_places=2, null=True, blank=True)
    cf_50 = models.DecimalField("50% cf", max_digits=5, decimal_places=2, null=True, blank=True)
    cef = models.DecimalField("cef", max_digits=5, decimal_places=2, null=True, blank=True)
    cef_50 = models.DecimalField("50% cef", max_digits=5, decimal_places=2, null=True, blank=True)
    ccf = models.DecimalField("ccf", max_digits=5, decimal_places=2, null=True, blank=True)
    ccf_30 = models.DecimalField("30% ccf", max_digits=5, decimal_places=2, null=True, blank=True)
    ceex = models.DecimalField("ceex", max_digits=5, decimal_places=2, null=True, blank=True)
    ceex_70 = models.DecimalField("70% ceex", max_digits=5, decimal_places=2, null=True, blank=True)
    cexf = models.DecimalField("cexf", max_digits=5, decimal_places=2, null=True, blank=True)
    special_cf = models.DecimalField("cf especial", max_digits=5, decimal_places=2, null=True, blank=True)
    special_ce = models.DecimalField("ce especial", max_digits=5, decimal_places=2, null=True, blank=True)
    approved = models.CharField("aprobado", max_length=1, blank=True)
    reproved = models.CharField("reprobado", max_length=1, blank=True)

    class Meta:
        ordering = ["enrollment", "subject__name"]
        unique_together = [("enrollment", "subject")]
        verbose_name = "evaluacion completiva"
        verbose_name_plural = "evaluaciones completivas"

    def __str__(self):
        return f"{self.enrollment.student} - {self.subject}"


class CurriculumInstitution(TimeStampedModel):
    description = models.CharField("descripcion", max_length=160, unique=True)
    deleted = models.BooleanField("eliminado", default=False)

    class Meta:
        ordering = ["description"]
        verbose_name = "institucion de curriculum"
        verbose_name_plural = "instituciones de curriculum"

    def __str__(self):
        return self.description


class CurriculumType(TimeStampedModel):
    description = models.CharField("descripcion", max_length=160, unique=True)

    class Meta:
        ordering = ["description"]
        verbose_name = "tipo de curriculum"
        verbose_name_plural = "tipos de curriculum"

    def __str__(self):
        return self.description


class Curriculum(TimeStampedModel):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name="curricula")
    administrative_employee = models.ForeignKey(
        AdministrativeEmployee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="curricula",
    )
    folder = models.CharField("carpeta", max_length=240, blank=True)

    class Meta:
        verbose_name = "curriculum"
        verbose_name_plural = "curricula"

    def __str__(self):
        owner = self.teacher or self.administrative_employee
        return f"Curriculum de {owner}" if owner else f"Curriculum {self.pk}"


class CurriculumDetail(TimeStampedModel):
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name="details")
    description = models.CharField("descripcion", max_length=240)
    date = models.DateField("fecha", null=True, blank=True)
    institution = models.ForeignKey(
        CurriculumInstitution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="curriculum_details",
    )
    curriculum_type = models.ForeignKey(
        CurriculumType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="curriculum_details",
    )
    file_url = models.CharField("archivo", max_length=300, blank=True)
    deleted = models.BooleanField("eliminado", default=False)

    class Meta:
        ordering = ["-date", "description"]
        verbose_name = "detalle de curriculum"
        verbose_name_plural = "detalles de curriculum"

    def __str__(self):
        return self.description
