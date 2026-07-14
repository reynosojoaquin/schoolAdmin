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
    photo_url = models.FileField("foto", upload_to="people/photos/", blank=True)
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

    @property
    def initials(self):
        first = self.first_name[:1] if self.first_name else ""
        last = self.last_name[:1] if self.last_name else ""
        return f"{first}{last}".upper() or "?"

    @property
    def photo_display_url(self):
        if not self.photo_url:
            return ""
        value = str(self.photo_url)
        if value.startswith(("http://", "https://", "/")):
            return value
        return self.photo_url.url


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
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="subjects",
        verbose_name="seccion",
    )
    name = models.CharField("nombre", max_length=120)
    weekly_hours = models.PositiveSmallIntegerField("horas semanales", default=0)
    responsible = models.ForeignKey(
        "Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_subjects",
        verbose_name="docente responsable",
    )

    class Meta:
        ordering = ["section__course__name", "section__name", "name"]
        unique_together = [("section", "name")]
        verbose_name = "asignatura"
        verbose_name_plural = "asignaturas"

    def __str__(self):
        return f"{self.name} - {self.section}"

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
        if self.section_id and self.subject_id and self.subject.section_id != self.section_id:
            raise ValidationError("La asignatura debe pertenecer a la misma seccion.")


class Student(PersonBase):
    sigerd_id = models.CharField("codigo SIGERD", max_length=40, blank=True)
    phone = models.CharField("telefono", max_length=30, blank=True)
    promoted = models.BooleanField("promovido", default=False)
    new_admission = models.BooleanField("nuevo ingreso", default=False)
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


class EquipmentCategory(TimeStampedModel):
    name = models.CharField("nombre", max_length=120, unique=True)
    description = models.TextField("descripcion", blank=True)
    active = models.BooleanField("activo", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria de equipo"
        verbose_name_plural = "categorias de equipos"

    def __str__(self):
        return self.name


class EquipmentItem(TimeStampedModel):
    STATUS_AVAILABLE = "available"
    STATUS_LOANED = "loaned"
    STATUS_MAINTENANCE = "maintenance"
    STATUS_RETIRED = "retired"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Disponible"),
        (STATUS_LOANED, "Prestado"),
        (STATUS_MAINTENANCE, "Mantenimiento"),
        (STATUS_RETIRED, "Retirado"),
    ]

    code = models.CharField("codigo", max_length=60, unique=True)
    name = models.CharField("nombre", max_length=160)
    category = models.ForeignKey(
        EquipmentCategory,
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name="categoria",
    )
    brand = models.CharField("marca", max_length=120, blank=True)
    model = models.CharField("modelo", max_length=120, blank=True)
    serial_number = models.CharField("numero de serie", max_length=120, blank=True)
    location = models.CharField("ubicacion", max_length=160, blank=True)
    acquisition_date = models.DateField("fecha de adquisicion", null=True, blank=True)
    status = models.CharField("estado", max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["name", "code"]
        verbose_name = "equipo"
        verbose_name_plural = "equipos"

    def __str__(self):
        return f"{self.name} ({self.code})"


class EquipmentLoan(TimeStampedModel):
    STATUS_ACTIVE = "active"
    STATUS_RETURNED = "returned"
    STATUS_OVERDUE = "overdue"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Activo"),
        (STATUS_RETURNED, "Devuelto"),
        (STATUS_OVERDUE, "Vencido"),
    ]

    item = models.ForeignKey(EquipmentItem, on_delete=models.PROTECT, related_name="loans", verbose_name="equipo")
    borrowed_by = models.ForeignKey(
        AdministrativeEmployee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipment_loans",
        verbose_name="empleado responsable",
    )
    borrower_name = models.CharField("recibido por", max_length=160)
    loan_date = models.DateField("fecha de prestamo")
    due_date = models.DateField("fecha de devolucion esperada", null=True, blank=True)
    return_date = models.DateField("fecha de devolucion", null=True, blank=True)
    status = models.CharField("estado", max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["-loan_date", "item__name"]
        verbose_name = "prestamo de equipo"
        verbose_name_plural = "prestamos de equipos"

    def __str__(self):
        return f"{self.item} - {self.borrower_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        new_status = EquipmentItem.STATUS_LOANED
        if self.status == self.STATUS_RETURNED or self.return_date:
            new_status = EquipmentItem.STATUS_AVAILABLE
        if self.item.status != new_status:
            self.item.status = new_status
            self.item.save(update_fields=["status", "updated_at"])


class ConsumableItem(TimeStampedModel):
    name = models.CharField("nombre", max_length=160, unique=True)
    category = models.CharField("categoria", max_length=120, blank=True)
    unit = models.CharField("unidad", max_length=40, default="unidad")
    quantity_available = models.DecimalField("existencia", max_digits=10, decimal_places=2, default=0)
    minimum_stock = models.DecimalField("minimo", max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField("activo", default=True)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "material gastable"
        verbose_name_plural = "materiales gastables"

    def __str__(self):
        return self.name

    @property
    def stock_status(self):
        if self.quantity_available <= 0:
            return "Agotado"
        if self.minimum_stock and self.quantity_available <= self.minimum_stock:
            return "Bajo"
        return "Disponible"


class ConsumableMovement(TimeStampedModel):
    TYPE_IN = "in"
    TYPE_OUT = "out"
    TYPE_ADJUSTMENT = "adjustment"
    TYPE_CHOICES = [
        (TYPE_IN, "Entrada"),
        (TYPE_OUT, "Salida"),
        (TYPE_ADJUSTMENT, "Ajuste"),
    ]

    item = models.ForeignKey(ConsumableItem, on_delete=models.PROTECT, related_name="movements", verbose_name="material")
    movement_type = models.CharField("tipo", max_length=20, choices=TYPE_CHOICES)
    quantity = models.DecimalField("cantidad", max_digits=10, decimal_places=2)
    date = models.DateField("fecha")
    delivered_to = models.CharField("entregado a", max_length=160, blank=True)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "movimiento de material gastable"
        verbose_name_plural = "movimientos de material gastable"

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.quantity} {self.item}"

    def quantity_delta(self):
        if self.movement_type == self.TYPE_OUT:
            return -self.quantity
        return self.quantity

    def save(self, *args, **kwargs):
        old_delta = 0
        if self.pk:
            old = ConsumableMovement.objects.select_related("item").get(pk=self.pk)
            old_delta = old.quantity_delta()
        super().save(*args, **kwargs)
        delta = self.quantity_delta() - old_delta
        if delta:
            self.item.quantity_available += delta
            self.item.save(update_fields=["quantity_available", "updated_at"])


class Expense(TimeStampedModel):
    PAYMENT_CASH = "cash"
    PAYMENT_TRANSFER = "transfer"
    PAYMENT_CHEQUE = "cheque"
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Efectivo"),
        (PAYMENT_TRANSFER, "Transferencia"),
        (PAYMENT_CHEQUE, "Cheque"),
    ]

    date = models.DateField("fecha")
    category = models.CharField("categoria", max_length=120)
    description = models.CharField("descripcion", max_length=240)
    vendor = models.CharField("proveedor", max_length=160, blank=True)
    amount = models.DecimalField("monto", max_digits=12, decimal_places=2)
    payment_method = models.CharField("forma de pago", max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    cheque_number = models.CharField("numero de cheque", max_length=60, blank=True)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "gasto"
        verbose_name_plural = "gastos"

    def __str__(self):
        return f"{self.date} - {self.description}"


class Cheque(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_DELIVERED = "delivered"
    STATUS_CLEARED = "cleared"
    STATUS_VOID = "void"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendiente"),
        (STATUS_DELIVERED, "Entregado"),
        (STATUS_CLEARED, "Cobrado"),
        (STATUS_VOID, "Anulado"),
    ]

    number = models.CharField("numero", max_length=60, unique=True)
    date = models.DateField("fecha")
    payee = models.CharField("beneficiario", max_length=180)
    concept = models.CharField("concepto", max_length=240)
    amount = models.DecimalField("monto", max_digits=12, decimal_places=2)
    status = models.CharField("estado", max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["-date", "number"]
        verbose_name = "cheque"
        verbose_name_plural = "cheques"

    def __str__(self):
        return f"Cheque {self.number} - {self.payee}"


class BankAccount(TimeStampedModel):
    name = models.CharField("nombre", max_length=160)
    bank_name = models.CharField("banco", max_length=160)
    account_number = models.CharField("numero de cuenta", max_length=80, unique=True)
    account_type = models.CharField("tipo de cuenta", max_length=80, blank=True)
    active = models.BooleanField("activa", default=True)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["bank_name", "name"]
        verbose_name = "cuenta bancaria"
        verbose_name_plural = "cuentas bancarias"

    def __str__(self):
        return f"{self.bank_name} - {self.name}"


class BankReconciliation(TimeStampedModel):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Abierta"),
        (STATUS_CLOSED, "Cerrada"),
    ]

    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
        related_name="reconciliations",
        verbose_name="cuenta bancaria",
    )
    period = models.CharField("periodo", max_length=20, help_text="Ejemplo: 2025-09")
    statement_balance = models.DecimalField("saldo banco", max_digits=12, decimal_places=2, default=0)
    book_balance = models.DecimalField("saldo libro", max_digits=12, decimal_places=2, default=0)
    deposits_in_transit = models.DecimalField("depositos en transito", max_digits=12, decimal_places=2, default=0)
    outstanding_checks = models.DecimalField("cheques pendientes", max_digits=12, decimal_places=2, default=0)
    bank_charges = models.DecimalField("cargos bancarios", max_digits=12, decimal_places=2, default=0)
    adjustments = models.DecimalField("ajustes", max_digits=12, decimal_places=2, default=0)
    status = models.CharField("estado", max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["-period", "bank_account__bank_name"]
        unique_together = [("bank_account", "period")]
        verbose_name = "conciliacion bancaria"
        verbose_name_plural = "conciliaciones bancarias"

    def __str__(self):
        return f"{self.bank_account} - {self.period}"

    @property
    def adjusted_bank_balance(self):
        return self.statement_balance + self.deposits_in_transit - self.outstanding_checks

    @property
    def adjusted_book_balance(self):
        return self.book_balance - self.bank_charges + self.adjustments

    @property
    def difference(self):
        return self.adjusted_bank_balance - self.adjusted_book_balance


class JournalEntry(TimeStampedModel):
    date = models.DateField("fecha")
    reference = models.CharField("referencia", max_length=80, blank=True)
    description = models.CharField("descripcion", max_length=240)
    debit_account = models.CharField("cuenta debito", max_length=160)
    credit_account = models.CharField("cuenta credito", max_length=160)
    amount = models.DecimalField("monto", max_digits=12, decimal_places=2)
    related_expense = models.ForeignKey(
        Expense,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_entries",
        verbose_name="gasto relacionado",
    )
    related_cheque = models.ForeignKey(
        Cheque,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_entries",
        verbose_name="cheque relacionado",
    )
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "asiento de diario"
        verbose_name_plural = "asientos de diario"

    def __str__(self):
        return f"{self.date} - {self.description}"


class StaffAssignment(TimeStampedModel):
    employee = models.ForeignKey(
        AdministrativeEmployee,
        on_delete=models.CASCADE,
        related_name="staff_assignments",
        verbose_name="empleado",
    )
    area = models.CharField("area", max_length=140)
    role = models.CharField("funcion", max_length=160)
    start_date = models.DateField("desde")
    end_date = models.DateField("hasta", null=True, blank=True)
    active = models.BooleanField("activo", default=True)
    notes = models.TextField("notas", blank=True)

    class Meta:
        ordering = ["employee__last_name", "employee__first_name", "area"]
        verbose_name = "asignacion de personal"
        verbose_name_plural = "asignaciones de personal"

    def __str__(self):
        return f"{self.employee} - {self.area}"


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
        on_delete=models.PROTECT,
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
        return f"{self.student} - {self.section} ({self.school_year})"

    def clean(self):
        if self.section_id and self.course_id and self.section.course_id != self.course_id:
            raise ValidationError("La seccion debe pertenecer al curso seleccionado.")


class Attendance(TimeStampedModel):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    STATUS_CHOICES = [
        (PRESENT, "Presente"),
        (ABSENT, "Ausente"),
        (LATE, "Tarde"),
        (EXCUSED, "Excusa"),
    ]

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name="inscripcion",
    )
    date = models.DateField("fecha")
    status = models.CharField("estado", max_length=12, choices=STATUS_CHOICES, default=PRESENT)
    note = models.CharField("nota", max_length=160, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_attendances",
        verbose_name="registrado por",
    )

    class Meta:
        ordering = ["-date", "enrollment__student__last_name", "enrollment__student__first_name"]
        unique_together = [("enrollment", "date")]
        verbose_name = "asistencia"
        verbose_name_plural = "asistencias"

    def __str__(self):
        return f"{self.enrollment.student} - {self.date} - {self.get_status_display()}"


class GuidanceCase(TimeStampedModel):
    TYPE_INCIDENT = "incident"
    TYPE_SUPPORT = "support"
    TYPE_REFERRAL = "referral"
    TYPE_FAMILY = "family"
    TYPE_CHOICES = [
        (TYPE_INCIDENT, "Incidencia"),
        (TYPE_SUPPORT, "Caso de apoyo"),
        (TYPE_REFERRAL, "Referimiento"),
        (TYPE_FAMILY, "Situacion familiar"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Baja"),
        (PRIORITY_MEDIUM, "Media"),
        (PRIORITY_HIGH, "Alta"),
        (PRIORITY_URGENT, "Urgente"),
    ]

    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_REFERRED = "referred"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Abierto"),
        (STATUS_IN_PROGRESS, "En seguimiento"),
        (STATUS_REFERRED, "Referido"),
        (STATUS_CLOSED, "Cerrado"),
    ]

    case_number = models.CharField("numero de caso", max_length=40, unique=True)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="guidance_cases", verbose_name="estudiante")
    case_type = models.CharField("tipo", max_length=20, choices=TYPE_CHOICES, default=TYPE_INCIDENT)
    priority = models.CharField("prioridad", max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField("estado", max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    opened_at = models.DateField("fecha de apertura")
    reported_by = models.CharField("reportado por", max_length=160, blank=True)
    referred_by_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referred_guidance_cases",
        verbose_name="docente que refiere",
    )
    assigned_to = models.ForeignKey(
        AdministrativeEmployee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_guidance_cases",
        verbose_name="orientador o psicologo responsable",
    )
    summary = models.TextField("descripcion del caso")
    initial_actions = models.TextField("acciones iniciales", blank=True)
    confidential = models.BooleanField("confidencial", default=True)
    closed_at = models.DateField("fecha de cierre", null=True, blank=True)
    closing_notes = models.TextField("notas de cierre", blank=True)

    class Meta:
        ordering = ["-opened_at", "-id"]
        verbose_name = "caso de orientacion"
        verbose_name_plural = "casos de orientacion"

    def __str__(self):
        return f"{self.case_number} - {self.student}"


class GuidanceFollowUp(TimeStampedModel):
    TYPE_INTERVIEW = "interview"
    TYPE_CALL = "call"
    TYPE_MEETING = "meeting"
    TYPE_HOME_VISIT = "home_visit"
    TYPE_REFERRAL = "referral"
    TYPE_OBSERVATION = "observation"
    TYPE_CHOICES = [
        (TYPE_INTERVIEW, "Entrevista"),
        (TYPE_CALL, "Llamada"),
        (TYPE_MEETING, "Reunion"),
        (TYPE_HOME_VISIT, "Visita domiciliaria"),
        (TYPE_REFERRAL, "Referimiento"),
        (TYPE_OBSERVATION, "Observacion"),
    ]

    guidance_case = models.ForeignKey(GuidanceCase, on_delete=models.CASCADE, related_name="followups", verbose_name="caso")
    date = models.DateField("fecha")
    intervention_type = models.CharField("tipo de seguimiento", max_length=20, choices=TYPE_CHOICES)
    attended_by = models.ForeignKey(
        AdministrativeEmployee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guidance_followups",
        verbose_name="atendido por",
    )
    participants = models.CharField("participantes", max_length=240, blank=True)
    notes = models.TextField("notas")
    next_steps = models.TextField("proximos pasos", blank=True)
    next_date = models.DateField("proxima fecha", null=True, blank=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "seguimiento de orientacion"
        verbose_name_plural = "seguimientos de orientacion"

    def __str__(self):
        return f"{self.guidance_case} - {self.date}"


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
