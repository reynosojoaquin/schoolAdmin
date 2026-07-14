from datetime import date

from django import forms
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Q

from .models import (
    AdministrativeEmployee,
    BankAccount,
    BankReconciliation,
    Cheque,
    ConsumableItem,
    ConsumableMovement,
    Course,
    EquipmentCategory,
    EquipmentItem,
    EquipmentLoan,
    Expense,
    GuidanceCase,
    GuidanceFollowUp,
    JournalEntry,
    Section,
    StaffAssignment,
    Student,
    Subject,
    Teacher,
    TeachingAssignment,
)


ACCESS_PERMISSION_CODES = [
    "manage_users_roles",
    "manage_people",
    "manage_academic_setup",
    "view_all_academic",
    "view_own_sections",
    "edit_grades",
    "import_grades",
    "view_grade_stats",
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
        "birthplace",
        "marital_status",
        "license_number",
        "photo_url",
    ]

    def apply_common_widgets(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        if "active" in self.fields:
            self.fields["active"].widget.attrs["class"] = "form-check-input"
        if "photo_url" in self.fields:
            self.fields["photo_url"].widget.attrs["accept"] = "image/*"


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


class TeacherForm(PersonFormMixin, forms.ModelForm):
    class Meta:
        model = Teacher
        fields = PersonFormMixin.common_fields + ["user"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_common_widgets()


class AdministrativeEmployeeForm(PersonFormMixin, forms.ModelForm):
    class Meta:
        model = AdministrativeEmployee
        fields = PersonFormMixin.common_fields + ["employee_type", "position"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_common_widgets()


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.filter(active=True).order_by("last_name", "first_name")
        self.fields["referred_by_teacher"].queryset = Teacher.objects.filter(active=True).order_by("last_name", "first_name")
        self.fields["assigned_to"].queryset = AdministrativeEmployee.objects.filter(active=True).order_by("last_name", "first_name")
        self.apply_widgets()


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
            "next_steps",
            "next_date",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "next_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, guidance_case=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["guidance_case"].queryset = GuidanceCase.objects.select_related("student").exclude(status=GuidanceCase.STATUS_CLOSED)
        self.fields["attended_by"].queryset = AdministrativeEmployee.objects.filter(active=True).order_by("last_name", "first_name")
        if guidance_case is not None:
            self.fields["guidance_case"].initial = guidance_case
            self.fields["guidance_case"].queryset = GuidanceCase.objects.filter(pk=guidance_case.pk)
            self.fields["guidance_case"].widget = forms.HiddenInput()
        self.apply_widgets()


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
            "responsible": "Docente guia",
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
        section_queryset = Section.objects.filter(active=True).select_related("course", "responsible")
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
        self.fields["section"].queryset = Section.objects.filter(active=True).select_related("course", "responsible")
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["section"].queryset = Section.objects.filter(active=True).select_related("course").order_by(
            "course__name",
            "name",
            "school_year",
        )
        self.fields["student"].queryset = Student.objects.filter(active=True).order_by("last_name", "first_name")
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
            is_enrolled = student.enrollments.filter(section=section, active=True).exists()
            if not is_enrolled:
                raise forms.ValidationError("El estudiante seleccionado no esta inscrito activamente en esa seccion.")
        return cleaned_data


class StudentImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Archivo Excel",
        help_text="Formato esperado: nombres, apellidos, cedula, sexo, sigerd, nacimiento, curso. Ejemplo de curso: 2A.",
    )
    school_year = forms.CharField(
        label="Ano escolar",
        max_length=20,
        initial=f"{date.today().year}-{date.today().year + 1}",
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
