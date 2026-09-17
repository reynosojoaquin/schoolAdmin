from datetime import date

from django import forms
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Q
from django.utils.crypto import get_random_string

from .models import (
    AdministrativeEmployee,
    BankAccount,
    BankReconciliation,
    Cheque,
    City,
    ConsumableItem,
    ConsumableMovement,
    Course,
    EquipmentCategory,
    EquipmentItem,
    EquipmentLoan,
    EmployeePosition,
    Expense,
    GuidanceCase,
    GuidanceFollowUp,
    JournalEntry,
    Phone,
    Section,
    StaffAssignment,
    Student,
    Subject,
    SystemConfiguration,
    Teacher,
    TeachingAssignment,
)


def configured_school_year():
    configuration = SystemConfiguration.get_solo()
    return configuration.current_school_year or f"{date.today().year}-{date.today().year + 1}"


class SystemConfigurationForm(forms.ModelForm):
    remove_logo = forms.BooleanField(
        label="Restablecer el logo inicial",
        required=False,
        help_text="Elimina el logo cargado y vuelve a mostrar el logo institucional incluido con el sistema.",
    )

    class Meta:
        model = SystemConfiguration
        fields = ["institution_name", "current_school_year", "logo"]
        widgets = {"logo": forms.FileInput()}
        labels = {
            "institution_name": "Nombre del centro educativo",
            "current_school_year": "Ano escolar actual",
            "logo": "Nuevo logo institucional",
        }
        help_texts = {
            "current_school_year": "Ejemplo: 2026-2027. Los usuarios veran por defecto solo este ano escolar.",
            "logo": "Formatos permitidos: PNG, JPG, JPEG o WebP. Tamano maximo: 4 MB.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["logo"].widget.attrs["accept"] = "image/png,image/jpeg,image/webp"
        self.fields["remove_logo"].widget.attrs["class"] = "form-check-input"

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        if not logo or not hasattr(logo, "content_type"):
            return logo
        if logo.size > 4 * 1024 * 1024:
            raise forms.ValidationError("El archivo supera el limite de 4 MB.")
        if logo.content_type not in {"image/png", "image/jpeg", "image/webp"}:
            raise forms.ValidationError("Selecciona una imagen PNG, JPG, JPEG o WebP valida.")
        return logo


ACCESS_PERMISSION_CODES = [
    "manage_users_roles",
    "manage_people",
    "manage_academic_setup",
    "view_all_academic",
    "view_own_sections",
    "edit_grades",
    "import_grades",
    "view_grade_stats",
    "view_all_school_years",
    # Coordinacion Administrativa
    "manage_admin_inventory",
    "manage_admin_consumables",
    "manage_admin_finance",
    "manage_admin_staff",
    # Orientacion
    "manage_guidance_cases",
    "view_all_people",
    # Coordinacion Academica
    "manage_registry_reports",
]


class PersonFormMixin:
    common_fields = [
        "first_name",
        "last_name",
        "document_id",
        "active",
        "email",
        "gender",
        "birth_date",
        "nationality",
        "birth_province",
        "birthplace",
        "marital_status",
        "license_number",
        "photo_url",
    ]

    def apply_common_widgets(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        for field_name in ("active", "is_guidance_counselor"):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs["class"] = "form-check-input"
        if "photo_url" in self.fields:
            self.fields["photo_url"].widget.attrs["accept"] = "image/*"
        if "nationality" in self.fields:
            self.fields["nationality"].empty_label = "Seleccione una nacionalidad"
        if "birth_province" in self.fields:
            self.fields["birth_province"].empty_label = "Seleccione una provincia"
            self.fields["birth_province"].widget.attrs["data-dependent-source"] = "birth-province"
        if "birthplace" in self.fields:
            self.fields["birthplace"].empty_label = "Seleccione primero una provincia"
            self.fields["birthplace"].widget.attrs["data-dependent-target"] = "birth-city"
            province_id = self.data.get("birth_province") if self.is_bound else None
            if not province_id and getattr(self.instance, "pk", None):
                province_id = self.instance.birth_province_id
                if not province_id and self.instance.birthplace_id:
                    province_id = self.instance.birthplace.province_id
                    self.initial["birth_province"] = province_id
            try:
                self.fields["birthplace"].queryset = City.objects.filter(
                    province_id=int(province_id)
                ) if province_id else City.objects.none()
            except (TypeError, ValueError):
                self.fields["birthplace"].queryset = City.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        province = cleaned_data.get("birth_province")
        city = cleaned_data.get("birthplace")
        if city and province and city.province_id != province.pk:
            self.add_error("birthplace", "La ciudad no pertenece a la provincia seleccionada.")
        return cleaned_data


class StudentForm(PersonFormMixin, forms.ModelForm):
    class Meta:
        model = Student
        fields = PersonFormMixin.common_fields + ["sigerd_id", "phone", "promoted", "new_admission", "sector"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_common_widgets()


class StudentTransferForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(active=True),
        label="Nuevo curso",
        empty_label="-- Seleccionar curso --",
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        label="Nueva seccion",
        empty_label="-- Seleccionar seccion --",
        required=False,
    )

    def __init__(self, *args, school_year=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school_year = school_year
        if self.initial.get("course_id"):
            course = Course.objects.filter(pk=self.initial["course_id"]).first()
            if course:
                self.fields["section"].queryset = Section.objects.filter(
                    course=course, school_year=school_year, active=True
                )

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get("course")
        section = cleaned_data.get("section")
        if course and section and section.course_id != course.pk:
            raise forms.ValidationError("La seccion debe pertenecer al curso seleccionado.")
        return cleaned_data


class TeacherForm(PersonFormMixin, forms.ModelForm):
    class Meta:
        model = Teacher
        fields = PersonFormMixin.common_fields + ["is_guidance_counselor", "user"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_common_widgets()


class AdministrativeEmployeeForm(PersonFormMixin, forms.ModelForm):
    phone = forms.CharField(label="Telefono", max_length=40, required=False)

    class Meta:
        model = AdministrativeEmployee
        fields = PersonFormMixin.common_fields + ["employee_type", "position"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and not self.is_bound:
            self.fields["phone"].initial = self.instance.phones.order_by("pk").values_list("number", flat=True).first()
        self.apply_common_widgets()
        self.fields["employee_type"].empty_label = "Seleccione un tipo de empleado"
        self.fields["employee_type"].widget.attrs["data-dependent-source"] = "employee-type"
        self.fields["position"].empty_label = "Seleccione primero un tipo de empleado"
        self.fields["position"].widget.attrs["data-dependent-target"] = "employee-position"
        employee_type_id = self.data.get("employee_type") if self.is_bound else None
        if not employee_type_id and getattr(self.instance, "pk", None):
            employee_type_id = self.instance.employee_type_id
        try:
            self.fields["position"].queryset = EmployeePosition.objects.filter(
                employee_type_id=int(employee_type_id)
            ) if employee_type_id else EmployeePosition.objects.none()
        except (TypeError, ValueError):
            self.fields["position"].queryset = EmployeePosition.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        employee_type = cleaned_data.get("employee_type")
        position = cleaned_data.get("position")
        if position and employee_type and position.employee_type_id != employee_type.pk:
            self.add_error("position", "La posición no pertenece al tipo de empleado seleccionado.")
        return cleaned_data

    def save(self, commit=True):
        employee = super().save(commit=commit)
        if commit:
            phone = self.cleaned_data.get("phone", "").strip()
            current = employee.phones.order_by("pk").first()
            if current:
                if phone:
                    current.number = phone
                    current.save(update_fields=["number"])
                else:
                    current.delete()
            elif phone:
                Phone.objects.create(administrative_employee=employee, number=phone)
        return employee


class AcademicFormMixin:
    def apply_widgets(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        if "active" in self.fields:
            self.fields["active"].widget.attrs["class"] = "form-check-input"


class AdministrationFormMixin:
    def apply_widgets(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        for field_name in ("active",):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs["class"] = "form-check-input"


class EquipmentCategoryForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = EquipmentCategory
        fields = ["name", "description", "active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_widgets()


class EquipmentItemForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = EquipmentItem
        fields = [
            "code",
            "name",
            "category",
            "brand",
            "model",
            "serial_number",
            "location",
            "acquisition_date",
            "status",
            "notes",
        ]
        widgets = {
            "acquisition_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = EquipmentCategory.objects.filter(active=True)
        self.apply_widgets()


class EquipmentLoanForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = EquipmentLoan
        fields = ["item", "borrowed_by", "borrower_name", "loan_date", "due_date", "return_date", "status", "notes"]
        widgets = {
            "loan_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "return_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = EquipmentItem.objects.exclude(status=EquipmentItem.STATUS_RETIRED)
        self.fields["borrowed_by"].queryset = AdministrativeEmployee.objects.filter(active=True)
        self.apply_widgets()


class ConsumableItemForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = ConsumableItem
        fields = ["name", "category", "unit", "quantity_available", "minimum_stock", "active", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_widgets()


class ConsumableMovementForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = ConsumableMovement
        fields = ["item", "movement_type", "quantity", "date", "delivered_to", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
        help_texts = {
            "quantity": "En ajustes puedes usar valores positivos o negativos.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = ConsumableItem.objects.filter(active=True)
        self.apply_widgets()


class ExpenseForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["date", "category", "description", "vendor", "amount", "payment_method", "cheque_number", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_widgets()


class ChequeForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = Cheque
        fields = ["number", "date", "payee", "concept", "amount", "status", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_widgets()


class BankAccountForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ["name", "bank_name", "account_number", "account_type", "active", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_widgets()


class BankReconciliationForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = BankReconciliation
        fields = [
            "bank_account",
            "period",
            "statement_balance",
            "book_balance",
            "deposits_in_transit",
            "outstanding_checks",
            "bank_charges",
            "adjustments",
            "status",
            "notes",
        ]
        help_texts = {
            "period": "Ejemplo: 2025-09.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bank_account"].queryset = BankAccount.objects.filter(active=True)
        self.apply_widgets()


class JournalEntryForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = [
            "date",
            "reference",
            "description",
            "debit_account",
            "credit_account",
            "amount",
            "related_expense",
            "related_cheque",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_widgets()


class StaffAssignmentForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = StaffAssignment
        fields = ["employee", "area", "role", "start_date", "end_date", "active", "notes"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].queryset = AdministrativeEmployee.objects.filter(active=True)
        self.apply_widgets()


class GuidanceCaseForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = GuidanceCase
        fields = [
            "case_number",
            "section",
            "student",
            "case_type",
            "priority",
            "status",
            "opened_at",
            "reported_by",
            "referred_by_teacher",
            "assigned_to",
            "summary",
            "initial_actions",
            "confidential",
            "closed_at",
            "closing_notes",
        ]
        widgets = {
            "opened_at": forms.DateInput(attrs={"type": "date"}),
            "closed_at": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        teacher = getattr(user, "teacher_profile", None)
        if not self.instance.pk:
            self.fields["case_number"].initial = f"ORI-{date.today():%Y%m%d}-{get_random_string(6).upper()}"
            self.fields["opened_at"].initial = date.today()
            self.fields["status"].initial = GuidanceCase.STATUS_OPEN
            self.fields["priority"].initial = GuidanceCase.PRIORITY_MEDIUM
            self.fields["case_type"].initial = GuidanceCase.TYPE_INCIDENT
            self.fields["confidential"].initial = True
        section_queryset = Section.objects.filter(
            active=True,
            school_year=configured_school_year(),
        ).select_related("course").order_by("course__name", "name", "school_year")
        if teacher and not user.is_superuser:
            section_queryset = section_queryset.filter(
                Q(responsible=teacher)
                | Q(teaching_assignments__teacher=teacher, teaching_assignments__active=True)
            ).distinct()
        self.fields["section"].queryset = section_queryset
        student_queryset = Student.objects.filter(active=True).order_by("last_name", "first_name")
        selected_section_id = self.data.get(self.add_prefix("section")) if self.is_bound else self.instance.section_id
        if selected_section_id:
            selected_section = Section.objects.filter(pk=selected_section_id).select_related("course").first()
            if selected_section:
                student_queryset = student_queryset.filter(
                    enrollments__course=selected_section.course,
                    enrollments__school_year=selected_section.school_year or configured_school_year(),
                    enrollments__active=True,
                ).distinct()
            else:
                student_queryset = Student.objects.none()
        else:
            student_queryset = Student.objects.none()
        self.fields["student"].queryset = student_queryset
        self.fields["referred_by_teacher"].queryset = Teacher.objects.filter(active=True).order_by("last_name", "first_name")
        assigned_queryset = Teacher.objects.filter(
            active=True,
            is_guidance_counselor=True,
        ).order_by("last_name", "first_name")
        if teacher and teacher.is_guidance_counselor and not user.is_superuser:
            assigned_queryset = assigned_queryset.filter(pk=teacher.pk)
            self.fields["assigned_to"].initial = teacher
        if teacher and not teacher.is_guidance_counselor and not user.is_superuser:
            self.fields["referred_by_teacher"].initial = teacher
            self.fields["reported_by"].initial = str(teacher)
            for field_name in [
                "case_number",
                "case_type",
                "priority",
                "status",
                "opened_at",
                "reported_by",
                "referred_by_teacher",
                "assigned_to",
                "initial_actions",
                "confidential",
                "closed_at",
                "closing_notes",
            ]:
                self.fields[field_name].widget = forms.HiddenInput()
                self.fields[field_name].required = False
            self.fields["section"].required = True
            self.fields["student"].required = True
        else:
            self.fields["section"].required = True
            self.fields["student"].required = True
        self.fields["assigned_to"].queryset = assigned_queryset
        self.apply_widgets()

    def clean(self):
        cleaned_data = super().clean()
        teacher = getattr(self.user, "teacher_profile", None)
        if not cleaned_data.get("case_number"):
            cleaned_data["case_number"] = f"ORI-{date.today():%Y%m%d}-{get_random_string(6).upper()}"
        section = cleaned_data.get("section")
        if teacher and section and not self.user.is_superuser:
            works_in_section = (
                section.responsible_id == teacher.pk
                or TeachingAssignment.objects.filter(teacher=teacher, section=section, active=True).exists()
            )
            if not works_in_section:
                raise forms.ValidationError("Solo puedes iniciar o tramitar casos en grados donde estas trabajando.")
        if teacher and teacher.is_guidance_counselor and not self.user.is_superuser:
            cleaned_data["assigned_to"] = teacher
        elif teacher and not self.user.is_superuser:
            cleaned_data["referred_by_teacher"] = teacher
            cleaned_data["reported_by"] = str(teacher)
            if self.instance.pk:
                cleaned_data["status"] = self.instance.status
                cleaned_data["priority"] = self.instance.priority
                cleaned_data["case_type"] = self.instance.case_type
                cleaned_data["opened_at"] = self.instance.opened_at
                cleaned_data["confidential"] = self.instance.confidential
                cleaned_data["assigned_to"] = self.instance.assigned_to
                cleaned_data["student"] = self.instance.student
                cleaned_data["initial_actions"] = self.instance.initial_actions
                cleaned_data["closed_at"] = self.instance.closed_at
                cleaned_data["closing_notes"] = self.instance.closing_notes
            else:
                cleaned_data["status"] = GuidanceCase.STATUS_OPEN
                cleaned_data["priority"] = GuidanceCase.PRIORITY_MEDIUM
                cleaned_data["case_type"] = GuidanceCase.TYPE_INCIDENT
                cleaned_data["opened_at"] = cleaned_data.get("opened_at") or date.today()
                cleaned_data["confidential"] = True
                cleaned_data["assigned_to"] = None
                cleaned_data["initial_actions"] = ""
                cleaned_data["closed_at"] = None
                cleaned_data["closing_notes"] = ""
            if section and cleaned_data.get("student"):
                is_enrolled = cleaned_data["student"].enrollments.filter(
                    course=section.course,
                    school_year=section.school_year or configured_school_year(),
                    active=True,
                ).exists()
                if not is_enrolled:
                    raise forms.ValidationError("El estudiante seleccionado no pertenece al curso de esa seccion.")
        elif not cleaned_data.get("student"):
            raise forms.ValidationError("Selecciona el estudiante relacionado con el caso.")
        if cleaned_data.get("student") and section:
            is_enrolled = cleaned_data["student"].enrollments.filter(
                course=section.course,
                school_year=section.school_year or configured_school_year(),
                active=True,
            ).exists()
            if not is_enrolled:
                raise forms.ValidationError("El estudiante seleccionado no pertenece al curso de esa seccion.")
        status = cleaned_data.get("status")
        closing_notes = (cleaned_data.get("closing_notes") or "").strip()
        if status == GuidanceCase.STATUS_CLOSED:
            if not closing_notes:
                raise forms.ValidationError("Para cerrar el caso debes escribir la explicacion del trabajo realizado.")
            if not cleaned_data.get("closed_at"):
                cleaned_data["closed_at"] = date.today()
        return cleaned_data


class GuidanceFollowUpForm(AdministrationFormMixin, forms.ModelForm):
    class Meta:
        model = GuidanceFollowUp
        fields = [
            "guidance_case",
            "date",
            "intervention_type",
            "attended_by",
            "participants",
            "notes",
            "evidence_file",
            "next_steps",
            "next_date",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "next_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, guidance_case=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        teacher = getattr(user, "teacher_profile", None)
        guidance_cases = GuidanceCase.objects.select_related("student").exclude(status=GuidanceCase.STATUS_CLOSED)
        if teacher and teacher.is_guidance_counselor and not user.is_superuser:
            guidance_cases = guidance_cases.filter(assigned_to=teacher)
        elif teacher and not user.is_superuser:
            guidance_cases = guidance_cases.none()
        self.fields["guidance_case"].queryset = guidance_cases
        attended_by_queryset = Teacher.objects.filter(
            active=True,
            is_guidance_counselor=True,
        ).order_by("last_name", "first_name")
        if teacher and teacher.is_guidance_counselor and not user.is_superuser:
            attended_by_queryset = attended_by_queryset.filter(pk=teacher.pk)
            self.fields["attended_by"].initial = teacher
            self.fields["attended_by"].widget = forms.HiddenInput()
        self.fields["attended_by"].queryset = attended_by_queryset
        if guidance_case is not None:
            self.fields["guidance_case"].initial = guidance_case
            self.fields["guidance_case"].queryset = GuidanceCase.objects.filter(pk=guidance_case.pk)
            self.fields["guidance_case"].widget = forms.HiddenInput()
        self.apply_widgets()

    def clean(self):
        cleaned_data = super().clean()
        teacher = getattr(self.user, "teacher_profile", None)
        guidance_case = cleaned_data.get("guidance_case")
        if teacher and not teacher.is_guidance_counselor and not self.user.is_superuser:
            raise forms.ValidationError("Los docentes pueden visualizar los seguimientos, pero no registrarlos.")
        if teacher and teacher.is_guidance_counselor and not self.user.is_superuser:
            cleaned_data["attended_by"] = teacher
            if guidance_case and guidance_case.assigned_to_id != teacher.pk:
                raise forms.ValidationError("Solo puedes registrar seguimiento en casos asignados a ti.")
        return cleaned_data


class CourseForm(AcademicFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "responsible", "active"]
        labels = {
            "name": "Curso o grado",
            "responsible": "Docente responsable del curso",
        }
        help_texts = {
            "name": "Ejemplo: 1, 2, 3, 4, 5 o 6.",
            "responsible": "Opcional. Usa este campo si el curso completo tiene un docente responsable.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible"].queryset = Teacher.objects.filter(active=True)
        self.apply_widgets()


class SectionForm(AcademicFormMixin, forms.ModelForm):
    class Meta:
        model = Section
        fields = ["course", "name", "school_year", "responsible", "active"]
        labels = {
            "name": "Seccion",
            "responsible": "Maestro encargado",
        }
        help_texts = {
            "name": "Ejemplo: A, B, C o D.",
            "school_year": "Ejemplo: 2025-2026.",
            "responsible": "Docente encargado directamente de esta seccion.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        course_queryset = Course.objects.filter(active=True)
        if self.instance and self.instance.pk:
            course_queryset = (course_queryset | Course.objects.filter(pk=self.instance.course_id)).distinct()
        self.fields["course"].queryset = course_queryset
        self.fields["responsible"].queryset = Teacher.objects.filter(active=True)
        self.fields["responsible"].required = True
        if not self.instance.pk:
            self.fields["school_year"].initial = configured_school_year()
        self.apply_widgets()


class SectionResponsibleForm(AcademicFormMixin, forms.ModelForm):
    class Meta:
        model = Section
        fields = ["responsible"]
        labels = {
            "responsible": "Maestro encargado",
        }
        help_texts = {
            "responsible": "Selecciona el docente que tendra a cargo esta seccion.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible"].queryset = Teacher.objects.filter(active=True)
        self.fields["responsible"].required = True
        self.apply_widgets()


class SubjectForm(AcademicFormMixin, forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["section", "name", "weekly_hours", "responsible"]
        labels = {
            "section": "Seccion",
            "weekly_hours": "Horas semanales",
            "responsible": "Docente responsable de la asignatura",
        }
        help_texts = {
            "section": "La asignatura queda disponible solo para esta seccion.",
            "weekly_hours": "Cantidad de horas de esta asignatura en la seccion.",
            "responsible": "Docente responsable general de esta asignatura en la seccion.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        section_queryset = Section.objects.filter(
            active=True,
            school_year=configured_school_year(),
        ).select_related("course", "responsible")
        if self.instance and self.instance.pk:
            section_queryset = (section_queryset | Section.objects.filter(pk=self.instance.section_id)).distinct()
        self.fields["section"].queryset = section_queryset
        self.fields["responsible"].queryset = Teacher.objects.filter(active=True)
        self.apply_widgets()


class TeachingAssignmentForm(AcademicFormMixin, forms.ModelForm):
    class Meta:
        model = TeachingAssignment
        fields = ["section", "subject", "teacher", "active"]
        labels = {
            "section": "Seccion",
            "subject": "Asignatura",
            "teacher": "Docente que imparte la asignatura",
        }
        help_texts = {
            "section": "Grupo especifico donde se impartira la asignatura.",
            "subject": "Debe pertenecer a la misma seccion seleccionada.",
            "teacher": "Este docente queda asignado a la asignatura en esa seccion.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["section"].queryset = Section.objects.filter(
            active=True,
            school_year=configured_school_year(),
        ).select_related("course", "responsible")
        self.fields["subject"].queryset = self.get_subject_queryset()
        self.fields["teacher"].queryset = Teacher.objects.filter(active=True)
        self.apply_widgets()

    def get_subject_queryset(self):
        queryset = Subject.objects.select_related("section", "section__course", "responsible")
        section_id = self.data.get("section") or self.initial.get("section")
        if not section_id and self.instance and self.instance.pk:
            section_id = self.instance.section_id

        if section_id:
            try:
                section = Section.objects.only("id").get(pk=section_id)
            except (Section.DoesNotExist, ValueError, TypeError):
                return queryset.none()
            return queryset.filter(section_id=section.id)

        if self.instance and self.instance.pk:
            return queryset.filter(Q(section_id=self.instance.section_id) | Q(pk=self.instance.subject_id))

        return queryset

    def clean(self):
        cleaned_data = super().clean()
        section = cleaned_data.get("section")
        subject = cleaned_data.get("subject")
        if section and subject and subject.section_id != section.id:
            raise forms.ValidationError(
                "La asignatura seleccionada pertenece a otra seccion. Selecciona una asignatura de la misma seccion."
            )
        return cleaned_data


class UserAccessForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        label="Roles",
        queryset=Group.objects.all().order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    teacher = forms.ModelChoiceField(
        label="Docente vinculado",
        queryset=Teacher.objects.filter(active=True).order_by("last_name", "first_name"),
        required=False,
        help_text="Solo se requiere para usuarios con rol Docente.",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff", "groups", "teacher"]
        labels = {
            "is_active": "Usuario activo",
            "is_staff": "Acceso al administrador Django",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        teacher = Teacher.objects.filter(user=self.instance).first() if self.instance.pk else None
        self.fields["teacher"].initial = teacher
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.setdefault("class", "form-control")
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"
        self.fields["is_staff"].widget.attrs["class"] = "form-check-input"

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            selected_teacher = self.cleaned_data.get("teacher")
            Teacher.objects.filter(user=user).exclude(pk=getattr(selected_teacher, "pk", None)).update(user=None)
            if selected_teacher:
                selected_teacher.user = user
                selected_teacher.save(update_fields=["user", "updated_at"])
        return user


class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        label="Funcionalidades",
        queryset=Permission.objects.filter(codename__in=ACCESS_PERMISSION_CODES).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]
        labels = {"name": "Nombre del rol"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.setdefault("class", "form-control")


class GradeImportForm(forms.Form):
    teaching_assignment = forms.ModelChoiceField(
        label="Seccion y asignatura",
        queryset=TeachingAssignment.objects.none(),
    )
    excel_file = forms.FileField(label="Archivo Excel")

    def __init__(self, *args, assignments=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teaching_assignment"].queryset = assignments if assignments is not None else TeachingAssignment.objects.none()
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class RegistryReportForm(forms.Form):
    REPORT_PERIODIC = "periodic"
    REPORT_RCF = "rcf"
    REPORT_FINAL_ACT = "final_act"
    REPORT_CHOICES = [
        (REPORT_PERIODIC, "Boletin de calificaciones por periodo"),
        (REPORT_RCF, "Reporte de calificaciones finales individual (RCF)"),
        (REPORT_FINAL_ACT, "Acta final colectiva"),
    ]
    SCOPE_GROUP = "group"
    SCOPE_STUDENT = "student"
    SCOPE_CHOICES = [
        (SCOPE_GROUP, "Colectivo por seccion"),
        (SCOPE_STUDENT, "Individual por estudiante"),
    ]

    report_type = forms.ChoiceField(label="Tipo de reporte", choices=REPORT_CHOICES)
    section = forms.ModelChoiceField(
        label="Seccion",
        queryset=Section.objects.none(),
        required=True,
    )
    scope = forms.ChoiceField(label="Alcance", choices=SCOPE_CHOICES, initial=SCOPE_GROUP)
    student = forms.ModelChoiceField(
        label="Estudiante",
        queryset=Student.objects.none(),
        required=False,
        help_text="Solo requerido para reportes individuales.",
    )

    def __init__(self, *args, school_year=None, **kwargs):
        super().__init__(*args, **kwargs)
        school_year = school_year or configured_school_year()
        self.fields["section"].queryset = Section.objects.filter(active=True).select_related("course").order_by(
            "course__name",
            "name",
            "school_year",
        )
        self.fields["section"].queryset = self.fields["section"].queryset.filter(school_year=school_year)
        self.fields["student"].queryset = Student.objects.filter(
            active=True,
            enrollments__school_year=school_year,
            enrollments__active=True,
        ).distinct().order_by("last_name", "first_name")
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned_data = super().clean()
        report_type = cleaned_data.get("report_type")
        scope = cleaned_data.get("scope")
        section = cleaned_data.get("section")
        student = cleaned_data.get("student")
        if report_type == self.REPORT_RCF:
            cleaned_data["scope"] = self.SCOPE_STUDENT
            if not student:
                raise forms.ValidationError("El RCF requiere seleccionar un estudiante.")
        if scope == self.SCOPE_STUDENT and not student:
            raise forms.ValidationError("Selecciona un estudiante para generar un reporte individual.")
        if report_type == self.REPORT_FINAL_ACT and scope == self.SCOPE_STUDENT:
            raise forms.ValidationError("El acta final se genera de forma colectiva por seccion.")
        if section and student:
            is_enrolled = student.enrollments.filter(course=section.course, active=True).exists()
            if not is_enrolled:
                raise forms.ValidationError("El estudiante seleccionado no esta inscrito activamente en el curso de esa seccion.")
        return cleaned_data


class StudentImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Archivo Excel",
        help_text="Formato esperado: nombres, apellidos, cedula, sexo, sigerd, nacimiento, curso. Ejemplo de curso: 2A.",
    )
    school_year = forms.CharField(
        label="Ano escolar",
        max_length=20,
        initial=configured_school_year,
    )
    update_existing = forms.BooleanField(
        label="Actualizar estudiantes existentes",
        required=False,
        initial=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        self.fields["update_existing"].widget.attrs["class"] = "form-check-input"

    def clean_excel_file(self):
        excel_file = self.cleaned_data["excel_file"]
        valid_extensions = (".xlsx", ".xlsm")
        if not excel_file.name.lower().endswith(valid_extensions):
            raise forms.ValidationError("Debe seleccionar un archivo Excel .xlsx o .xlsm.")
        return excel_file
