from datetime import date

from django import forms
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Q

from .models import AdministrativeEmployee, Course, Section, Student, Subject, Teacher, TeachingAssignment


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


class StudentForm(PersonFormMixin, forms.ModelForm):
    class Meta:
        model = Student
        fields = PersonFormMixin.common_fields + ["sigerd_id", "phone", "sector"]
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
        course_queryset = Course.objects.filter(active=True, sections__isnull=False).distinct()
        if self.instance and self.instance.pk:
            course_queryset = (course_queryset | Course.objects.filter(pk=self.instance.course_id)).distinct()
        self.fields["course"].queryset = course_queryset
        self.fields["responsible"].queryset = Teacher.objects.filter(active=True)
        self.apply_widgets()


class SubjectForm(AcademicFormMixin, forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["course", "name", "responsible"]
        labels = {
            "responsible": "Docente responsable de la asignatura",
        }
        help_texts = {
            "course": "La asignatura queda disponible para las secciones de este curso.",
            "responsible": "Docente responsable general de esta asignatura en el curso.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.filter(active=True)
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
            "subject": "Debe pertenecer al mismo curso de la seccion seleccionada.",
            "teacher": "Este docente queda asignado a la asignatura en esa seccion.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["section"].queryset = Section.objects.filter(active=True).select_related("course", "responsible")
        self.fields["subject"].queryset = self.get_subject_queryset()
        self.fields["teacher"].queryset = Teacher.objects.filter(active=True)
        self.apply_widgets()

    def get_subject_queryset(self):
        queryset = Subject.objects.select_related("course", "responsible").filter(course__sections__isnull=False).distinct()
        section_id = self.data.get("section") or self.initial.get("section")
        if not section_id and self.instance and self.instance.pk:
            section_id = self.instance.section_id

        if section_id:
            try:
                section = Section.objects.only("course_id").get(pk=section_id)
            except (Section.DoesNotExist, ValueError, TypeError):
                return queryset.none()
            return queryset.filter(course_id=section.course_id)

        if self.instance and self.instance.pk:
            return queryset.filter(Q(course_id=self.instance.section.course_id) | Q(pk=self.instance.subject_id))

        return queryset

    def clean(self):
        cleaned_data = super().clean()
        section = cleaned_data.get("section")
        subject = cleaned_data.get("subject")
        if section and subject and section.course_id != subject.course_id:
            raise forms.ValidationError(
                "La asignatura seleccionada pertenece a otro curso. Selecciona una asignatura del mismo curso de la seccion."
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
