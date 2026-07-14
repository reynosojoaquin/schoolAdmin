from datetime import date
from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.db.models import Avg, Count
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from openpyxl import Workbook, load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

from .forms import (
    AdministrativeEmployeeForm,
    BankAccountForm,
    BankReconciliationForm,
    ChequeForm,
    ConsumableItemForm,
    ConsumableMovementForm,
    CourseForm,
    EquipmentCategoryForm,
    EquipmentItemForm,
    EquipmentLoanForm,
    ExpenseForm,
    GradeImportForm,
    GuidanceCaseForm,
    GuidanceFollowUpForm,
    JournalEntryForm,
    RegistryReportForm,
    RoleForm,
    SectionForm,
    StaffAssignmentForm,
    StudentForm,
    StudentImportForm,
    SubjectForm,
    TeacherForm,
    TeachingAssignmentForm,
    UserAccessForm,
)
from .importers import commit_student_import, read_student_rows_from_excel
from .models import (
    AdministrativeEmployee,
    Attendance,
    BankAccount,
    BankReconciliation,
    Cheque,
    Competency,
    ConsumableItem,
    ConsumableMovement,
    Course,
    EquipmentCategory,
    EquipmentItem,
    EquipmentLoan,
    Enrollment,
    Expense,
    Grade,
    GradeCompletion,
    GuidanceCase,
    GuidanceFollowUp,
    JournalEntry,
    Section,
    StaffAssignment,
    Student,
    Subject,
    SubjectCompetency,
    Teacher,
    TeachingAssignment,
)
from .report_pdfs import build_final_act_pdf, build_periodic_report_pdf, build_rcf_report_pdf


ADMIN_ROLE = "Administrador"
TEACHER_ROLE = "Docente"
READ_ROLE = "Consulta"
MANAGE_USERS = "core.manage_users_roles"
MANAGE_PEOPLE = "core.manage_people"
MANAGE_ACADEMIC = "core.manage_academic_setup"
VIEW_ALL_ACADEMIC = "core.view_all_academic"
VIEW_OWN_SECTIONS = "core.view_own_sections"
EDIT_GRADES = "core.edit_grades"
IMPORT_GRADES = "core.import_grades"
VIEW_GRADE_STATS = "core.view_grade_stats"


def has_role(user, role_name):
    return user.is_authenticated and user.groups.filter(name=role_name).exists()


def is_admin_user(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm(MANAGE_USERS))


def is_teacher_user(user):
    return user.is_authenticated and user.has_perm(VIEW_OWN_SECTIONS) and hasattr(user, "teacher_profile")


def can_manage(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm(MANAGE_USERS))


def can_manage_people(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm(MANAGE_PEOPLE))


def can_manage_administration(user):
    return user.is_authenticated and (
        user.is_superuser or user.has_perm(MANAGE_PEOPLE) or user.has_perm(MANAGE_USERS)
    )


def can_manage_guidance(user):
    return user.is_authenticated and (
        user.is_superuser or user.has_perm(MANAGE_PEOPLE) or user.has_perm(VIEW_ALL_ACADEMIC)
    )


def can_manage_academic(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm(MANAGE_ACADEMIC))


def can_view_all_academic(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm(VIEW_ALL_ACADEMIC))


def can_edit_grades(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm(EDIT_GRADES))


def can_import_grades(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm(IMPORT_GRADES))


def can_view_grade_stats(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm(VIEW_GRADE_STATS))


def visible_assignments_for_user(user):
    queryset = TeachingAssignment.objects.filter(active=True).select_related(
        "section",
        "section__course",
        "subject",
        "teacher",
    )
    if can_view_all_academic(user):
        return queryset
    if is_teacher_user(user):
        return queryset.filter(teacher=user.teacher_profile)
    return queryset.none()


def visible_grades_for_user(user):
    assignments = visible_assignments_for_user(user)
    grade_filter = None
    for assignment in assignments:
        condition = Q(enrollment__section=assignment.section, subject=assignment.subject)
        grade_filter = condition if grade_filter is None else grade_filter | condition
    if grade_filter is None:
        return Grade.objects.none()
    return Grade.objects.filter(grade_filter).select_related(
        "enrollment__student",
        "enrollment__course",
        "enrollment__section",
        "subject__section",
        "subject__section__course",
        "subject",
    ).distinct()


class ManagementAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return can_manage(self.request.user)


class PeopleAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return can_manage_people(self.request.user)


class AdministrationAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return can_manage_administration(self.request.user)


class GuidanceAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return can_manage_guidance(self.request.user)


class AcademicSetupAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return can_manage_academic(self.request.user)


class AcademicAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return can_view_all_academic(self.request.user) or is_teacher_user(self.request.user)


@login_required
def dashboard(request):
    if is_teacher_user(request.user) and not is_admin_user(request.user):
        assignments = visible_assignments_for_user(request.user)
        context = {
            "teacher_mode": True,
            "assignment_count": assignments.count(),
            "section_count": assignments.values("section_id").distinct().count(),
            "grade_count": visible_grades_for_user(request.user).count(),
        }
        return render(request, "core/dashboard.html", context)

    context = {
        "student_count": Student.objects.filter(active=True).count(),
        "teacher_count": Teacher.objects.filter(active=True).count(),
        "employee_count": AdministrativeEmployee.objects.filter(active=True).count(),
        "course_count": Course.objects.filter(active=True).count(),
        "section_count": Section.objects.filter(active=True).count(),
        "subject_count": Subject.objects.count(),
        "assignment_count": TeachingAssignment.objects.filter(active=True).count(),
        "enrollment_count": Enrollment.objects.filter(active=True).count(),
        "grade_count": Grade.objects.count(),
    }
    return render(request, "core/dashboard.html", context)


class PersonListView(PeopleAccessMixin, ListView):
    template_name = "core/people_list.html"
    paginate_by = 20
    search_placeholder = "Buscar..."
    create_url_name = ""
    edit_url_name = ""
    section_label = ""

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(document_id__icontains=query)
                | Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["title"] = self.title
        context["section_label"] = self.section_label
        context["create_url_name"] = self.create_url_name
        context["edit_url_name"] = self.edit_url_name
        context["import_url_name"] = getattr(self, "import_url_name", "")
        context["search_placeholder"] = self.search_placeholder
        return context


class PersonCreateView(PeopleAccessMixin, CreateView):
    template_name = "core/person_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class PersonUpdateView(PeopleAccessMixin, UpdateView):
    template_name = "core/person_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class AcademicListView(AcademicSetupAccessMixin, ListView):
    template_name = "core/academic_list.html"
    paginate_by = 20
    search_placeholder = "Buscar..."
    create_url_name = ""
    edit_url_name = ""
    section_label = "Gestion academica"
    columns = []

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["title"] = self.title
        context["section_label"] = self.section_label
        context["create_url_name"] = self.create_url_name
        context["edit_url_name"] = self.edit_url_name
        context["search_placeholder"] = self.search_placeholder
        context["columns"] = self.columns
        context["row_actions"] = getattr(self, "row_actions", [])
        return context


class AcademicCreateView(AcademicSetupAccessMixin, CreateView):
    template_name = "core/academic_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class AcademicUpdateView(AcademicSetupAccessMixin, UpdateView):
    template_name = "core/academic_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class AcademicDeleteView(AcademicSetupAccessMixin, DeleteView):
    template_name = "core/confirm_delete.html"
    title = "Eliminar registro"
    cancel_url_name = ""
    protected_message = "No se puede eliminar este registro porque tiene informacion relacionada."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        context["related_summary"] = self.get_related_summary()
        return context

    def get_related_summary(self):
        return []

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(request, self.protected_message)
            return redirect(self.success_url)
        messages.success(request, "Registro eliminado correctamente.")
        return redirect(self.success_url)


class AdministrationListView(AdministrationAccessMixin, ListView):
    template_name = "core/academic_list.html"
    paginate_by = 20
    search_placeholder = "Buscar..."
    create_url_name = ""
    edit_url_name = ""
    section_label = "Administracion"
    columns = []

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["title"] = self.title
        context["section_label"] = self.section_label
        context["create_url_name"] = self.create_url_name
        context["edit_url_name"] = self.edit_url_name
        context["search_placeholder"] = self.search_placeholder
        context["columns"] = self.columns
        return context


class AdministrationCreateView(AdministrationAccessMixin, CreateView):
    template_name = "core/academic_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class AdministrationUpdateView(AdministrationAccessMixin, UpdateView):
    template_name = "core/academic_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class GuidanceListView(GuidanceAccessMixin, ListView):
    template_name = "core/academic_list.html"
    paginate_by = 20
    search_placeholder = "Buscar..."
    create_url_name = ""
    edit_url_name = ""
    section_label = "Orientacion y psicologia"
    columns = []
    row_actions = []

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["title"] = self.title
        context["section_label"] = self.section_label
        context["create_url_name"] = self.create_url_name
        context["edit_url_name"] = self.edit_url_name
        context["search_placeholder"] = self.search_placeholder
        context["columns"] = self.columns
        context["row_actions"] = self.row_actions
        return context


class GuidanceCreateView(GuidanceAccessMixin, CreateView):
    template_name = "core/academic_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class GuidanceUpdateView(GuidanceAccessMixin, UpdateView):
    template_name = "core/academic_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class StudentListView(PersonListView):
    model = Student
    title = "Estudiantes"
    section_label = "Gestion de estudiantes"
    create_url_name = "core:student_create"
    edit_url_name = "core:student_update"
    import_url_name = "core:student_import"
    search_placeholder = "Buscar por nombre, cedula o correo"


class StudentCreateView(PersonCreateView):
    model = Student
    form_class = StudentForm
    title = "Nuevo estudiante"
    success_url = reverse_lazy("core:student_list")
    cancel_url_name = "core:student_list"


class StudentUpdateView(PersonUpdateView):
    model = Student
    form_class = StudentForm
    title = "Editar estudiante"
    success_url = reverse_lazy("core:student_list")
    cancel_url_name = "core:student_list"


class StudentImportView(LoginRequiredMixin, View):
    template_name = "core/student_import.html"
    session_key = "student_import_preview"

    def get(self, request):
        form = StudentImportForm()
        request.session.pop(self.session_key, None)
        return render(request, self.template_name, {"form": form, "preview": None, "result": None})

    def post(self, request):
        action = request.POST.get("action", "preview")

        if action == "cancel":
            request.session.pop(self.session_key, None)
            form = StudentImportForm()
            return render(request, self.template_name, {"form": form, "preview": None, "result": None})

        if action == "confirm":
            saved_preview = request.session.get(self.session_key)
            if not saved_preview:
                form = StudentImportForm()
                form.add_error(None, "No hay una vista previa pendiente. Selecciona el archivo nuevamente.")
                return render(request, self.template_name, {"form": form, "preview": None, "result": None})

            result = commit_student_import(
                saved_preview["rows"],
                school_year=saved_preview["school_year"],
                update_existing=saved_preview["update_existing"],
            )
            request.session.pop(self.session_key, None)
            form = StudentImportForm()
            return render(request, self.template_name, {"form": form, "preview": None, "result": result})

        form = StudentImportForm(request.POST, request.FILES)
        if form.is_valid():
            preview = read_student_rows_from_excel(
                form.cleaned_data["excel_file"],
                update_existing=form.cleaned_data["update_existing"],
            )
            if not preview.rows:
                return render(request, self.template_name, {"form": form, "preview": preview, "result": None})

            request.session[self.session_key] = {
                "rows": preview.rows,
                "school_year": form.cleaned_data["school_year"],
                "update_existing": form.cleaned_data["update_existing"],
            }
            request.session.modified = True
            return render(request, self.template_name, {"form": form, "preview": preview, "result": None})

        return render(request, self.template_name, {"form": form, "preview": None, "result": None})


class CourseListView(AcademicListView):
    model = Course
    title = "Cursos"
    create_url_name = "core:course_create"
    edit_url_name = "core:course_update"
    search_placeholder = "Buscar curso"
    columns = [
        ("name", "Curso"),
        ("responsible", "Responsable"),
        ("active", "Estado"),
        ("students", "Estudiantes"),
    ]
    row_actions = [
        ("Editar", "core:course_update"),
        ("Eliminar", "core:course_delete"),
    ]

    def get_queryset(self):
        queryset = Course.objects.select_related("responsible")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(name__icontains=query)
            | Q(responsible__first_name__icontains=query)
            | Q(responsible__last_name__icontains=query)
        )


class CourseCreateView(AcademicCreateView):
    model = Course
    form_class = CourseForm
    title = "Nuevo curso"
    success_url = reverse_lazy("core:course_list")
    cancel_url_name = "core:course_list"


class CourseUpdateView(AcademicUpdateView):
    model = Course
    form_class = CourseForm
    title = "Editar curso"
    success_url = reverse_lazy("core:course_list")
    cancel_url_name = "core:course_list"


class CourseDeleteView(AcademicDeleteView):
    model = Course
    title = "Eliminar curso"
    success_url = reverse_lazy("core:course_list")
    cancel_url_name = "core:course_list"
    protected_message = "No se puede eliminar este curso porque tiene inscripciones o asignaturas relacionadas."

    def get_related_summary(self):
        return [
            ("Secciones", self.object.sections.count()),
            ("Asignaturas", Subject.objects.filter(section__course=self.object).count()),
            ("Inscripciones", self.object.enrollments.count()),
        ]


class CourseStudentsView(AcademicSetupAccessMixin, ListView):
    template_name = "core/enrollment_students.html"
    paginate_by = 30

    def get_queryset(self):
        self.course = Course.objects.get(pk=self.kwargs["pk"])
        queryset = Enrollment.objects.filter(course=self.course, active=True).select_related("student", "course", "section")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(student__first_name__icontains=query)
                | Q(student__last_name__icontains=query)
                | Q(student__document_id__icontains=query)
                | Q(section__name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["title"] = f"Estudiantes del curso {self.course}"
        context["group_label"] = "Curso"
        context["group_value"] = self.course
        context["back_url_name"] = "core:course_list"
        return context


class SectionListView(AcademicListView):
    model = Section
    title = "Secciones"
    create_url_name = "core:section_create"
    edit_url_name = "core:section_update"
    search_placeholder = "Buscar por curso, seccion, ano o docente"
    columns = [
        ("course", "Curso"),
        ("name", "Seccion"),
        ("school_year", "Ano escolar"),
        ("responsible", "Docente guia"),
        ("active", "Estado"),
        ("students", "Estudiantes"),
        ("assignments", "Asignaturas/docentes"),
    ]
    row_actions = [
        ("Editar", "core:section_update"),
        ("Eliminar", "core:section_delete"),
    ]

    def get_queryset(self):
        queryset = Section.objects.select_related("course", "responsible")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(name__icontains=query)
            | Q(course__name__icontains=query)
            | Q(school_year__icontains=query)
            | Q(responsible__first_name__icontains=query)
            | Q(responsible__last_name__icontains=query)
        )


class SectionCreateView(AcademicCreateView):
    model = Section
    form_class = SectionForm
    title = "Nueva seccion"
    success_url = reverse_lazy("core:section_list")
    cancel_url_name = "core:section_list"


class SectionUpdateView(AcademicUpdateView):
    model = Section
    form_class = SectionForm
    title = "Editar seccion"
    success_url = reverse_lazy("core:section_list")
    cancel_url_name = "core:section_list"


class SectionDeleteView(AcademicDeleteView):
    model = Section
    title = "Eliminar seccion"
    success_url = reverse_lazy("core:section_list")
    cancel_url_name = "core:section_list"

    def get_related_summary(self):
        return [
            ("Estudiantes inscritos", self.object.enrollments.count()),
            ("Asignaciones docentes", self.object.teaching_assignments.count()),
        ]


class SectionStudentsView(AcademicSetupAccessMixin, ListView):
    template_name = "core/enrollment_students.html"
    paginate_by = 30

    def get_queryset(self):
        self.section = Section.objects.select_related("course").get(pk=self.kwargs["pk"])
        queryset = Enrollment.objects.filter(section=self.section, active=True).select_related("student", "course", "section")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(student__first_name__icontains=query)
                | Q(student__last_name__icontains=query)
                | Q(student__document_id__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["title"] = f"Estudiantes de la seccion {self.section}"
        context["group_label"] = "Seccion"
        context["group_value"] = self.section
        context["back_url_name"] = "core:section_list"
        return context


def course_number(course):
    digits = "".join(ch for ch in course.name if ch.isdigit())
    return int(digits) if digits else None


def previous_course_for_section(section):
    number = course_number(section.course)
    if not number or number <= 1:
        return None
    return Course.objects.filter(name=str(number - 1)).first()


class SectionEnrollmentView(AcademicSetupAccessMixin, View):
    template_name = "core/section_enrollment.html"

    def get_section(self):
        return get_object_or_404(Section.objects.select_related("course"), pk=self.kwargs["pk"])

    def get_candidates(self, section):
        already_enrolled = Enrollment.objects.filter(
            school_year=section.school_year,
            active=True,
        ).values("student_id")
        filters = Q(new_admission=True)
        previous_course = previous_course_for_section(section)
        if previous_course:
            filters |= Q(
                promoted=True,
                enrollments__course=previous_course,
                enrollments__active=True,
            )

        queryset = (
            Student.objects.filter(active=True)
            .filter(filters)
            .exclude(pk__in=already_enrolled)
            .distinct()
            .order_by("last_name", "first_name", "id")
        )
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(document_id__icontains=query)
                | Q(sigerd_id__icontains=query)
            )
        return queryset

    def render_page(self, request, section):
        candidates = self.get_candidates(section)
        return render(
            request,
            self.template_name,
            {
                "section": section,
                "previous_course": previous_course_for_section(section),
                "query": request.GET.get("q", "").strip(),
                "candidates": candidates[:200],
                "candidate_count": candidates.count(),
            },
        )

    def get(self, request, *args, **kwargs):
        return self.render_page(request, self.get_section())

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        section = self.get_section()
        student_ids = request.POST.getlist("students")
        if not student_ids:
            messages.error(request, "Selecciona al menos un estudiante para inscribir.")
            return self.render_page(request, section)

        candidate_ids = set(str(pk) for pk in self.get_candidates(section).values_list("pk", flat=True))
        selected_ids = [student_id for student_id in student_ids if student_id in candidate_ids]
        students = Student.objects.filter(pk__in=selected_ids, active=True)
        enrolled_count = 0
        for student in students:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=section.course,
                school_year=section.school_year,
                defaults={"section": section, "active": True},
            )
            if not created and enrollment.section_id != section.id:
                enrollment.section = section
                enrollment.active = True
                enrollment.save(update_fields=["section", "active"])
            elif not created and not enrollment.active:
                enrollment.active = True
                enrollment.save(update_fields=["active"])

            student.promoted = False
            student.new_admission = False
            student.save(update_fields=["promoted", "new_admission"])
            enrolled_count += 1

        messages.success(request, f"Se inscribieron {enrolled_count} estudiantes en {section}.")
        return redirect("core:section_students", pk=section.pk)


class SectionAttendanceView(AcademicAccessMixin, View):
    template_name = "core/section_attendance.html"

    def get_section(self):
        section_queryset = Section.objects.select_related("course")
        if not can_view_all_academic(self.request.user):
            section_ids = visible_assignments_for_user(self.request.user).values("section_id")
            section_queryset = section_queryset.filter(pk__in=section_ids)
        return get_object_or_404(section_queryset, pk=self.kwargs["pk"])

    def get_attendance_date(self):
        raw_date = self.request.GET.get("date") or self.request.POST.get("date")
        if raw_date:
            try:
                return date.fromisoformat(raw_date)
            except ValueError:
                return date.today()
        return date.today()

    def get_enrollments(self, section):
        return (
            Enrollment.objects.filter(section=section, active=True)
            .select_related("student")
            .order_by("student__last_name", "student__first_name", "student__id")
        )

    def build_rows(self, section, attendance_date):
        enrollments = self.get_enrollments(section)
        attendance_by_enrollment = {
            attendance.enrollment_id: attendance
            for attendance in Attendance.objects.filter(enrollment__in=enrollments, date=attendance_date)
        }
        rows = []
        for enrollment in enrollments:
            attendance = attendance_by_enrollment.get(enrollment.id)
            rows.append(
                {
                    "enrollment": enrollment,
                    "attendance": attendance,
                    "status": attendance.status if attendance else Attendance.PRESENT,
                    "note": attendance.note if attendance else "",
                }
            )
        return rows

    def render_page(self, request, section, attendance_date):
        rows = self.build_rows(section, attendance_date)
        status_counts = {choice: 0 for choice, _ in Attendance.STATUS_CHOICES}
        for row in rows:
            status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
        return render(
            request,
            self.template_name,
            {
                "section": section,
                "attendance_date": attendance_date,
                "rows": rows,
                "status_choices": Attendance.STATUS_CHOICES,
                "status_counts": status_counts,
            },
        )

    def get(self, request, *args, **kwargs):
        section = self.get_section()
        return self.render_page(request, section, self.get_attendance_date())

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        section = self.get_section()
        attendance_date = self.get_attendance_date()
        enrollments = self.get_enrollments(section)
        saved_count = 0

        for enrollment in enrollments:
            status = request.POST.get(f"status_{enrollment.id}", Attendance.PRESENT)
            if status not in dict(Attendance.STATUS_CHOICES):
                status = Attendance.PRESENT
            note = request.POST.get(f"note_{enrollment.id}", "").strip()[:160]
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=attendance_date,
                defaults={
                    "status": status,
                    "note": note,
                    "recorded_by": request.user,
                },
            )
            saved_count += 1

        messages.success(request, f"Asistencia guardada para {saved_count} estudiantes.")
        return redirect(f"{request.path}?date={attendance_date.isoformat()}")


class SectionTeachingAssignmentsView(AcademicSetupAccessMixin, ListView):
    template_name = "core/section_assignments.html"
    paginate_by = 30

    def get_queryset(self):
        self.section = Section.objects.select_related("course", "responsible").get(pk=self.kwargs["pk"])
        queryset = TeachingAssignment.objects.filter(section=self.section).select_related(
            "section",
            "section__course",
            "subject",
            "teacher",
        )
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(subject__name__icontains=query)
                | Q(teacher__first_name__icontains=query)
                | Q(teacher__last_name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["section"] = self.section
        context["title"] = f"Docencia de la seccion {self.section}"
        return context


class SubjectListView(AcademicListView):
    model = Subject
    title = "Asignaturas"
    create_url_name = "core:subject_create"
    edit_url_name = "core:subject_update"
    search_placeholder = "Buscar por asignatura, seccion, curso o responsable"
    columns = [
        ("name", "Asignatura"),
        ("section", "Seccion"),
        ("weekly_hours", "Horas"),
        ("responsible", "Responsable"),
    ]
    row_actions = [
        ("Editar", "core:subject_update"),
        ("Eliminar", "core:subject_delete"),
    ]

    def get_queryset(self):
        queryset = (
            Subject.objects.select_related("section", "section__course", "responsible")
            .distinct()
        )
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(name__icontains=query)
            | Q(section__name__icontains=query)
            | Q(section__course__name__icontains=query)
            | Q(section__school_year__icontains=query)
            | Q(responsible__first_name__icontains=query)
            | Q(responsible__last_name__icontains=query)
        )


class SubjectCreateView(AcademicCreateView):
    model = Subject
    form_class = SubjectForm
    title = "Nueva asignatura"
    success_url = reverse_lazy("core:subject_list")
    cancel_url_name = "core:subject_list"


class SubjectUpdateView(AcademicUpdateView):
    model = Subject
    form_class = SubjectForm
    title = "Editar asignatura"
    success_url = reverse_lazy("core:subject_list")
    cancel_url_name = "core:subject_list"


class SubjectDeleteView(AcademicDeleteView):
    model = Subject
    title = "Eliminar asignatura"
    success_url = reverse_lazy("core:subject_list")
    cancel_url_name = "core:subject_list"
    protected_message = "No se puede eliminar esta asignatura porque tiene calificaciones relacionadas."

    def get_related_summary(self):
        return [
            ("Asignaciones docentes", self.object.teaching_assignments.count()),
            ("Calificaciones", self.object.grades.count()),
            ("Competencias", self.object.subject_competencies.count()),
        ]


class TeachingAssignmentListView(AcademicListView):
    model = TeachingAssignment
    title = "Asignaciones docentes"
    create_url_name = "core:teaching_assignment_create"
    edit_url_name = "core:teaching_assignment_update"
    search_placeholder = "Buscar por seccion, asignatura o docente"
    columns = [
        ("section", "Seccion"),
        ("subject", "Asignatura"),
        ("teacher", "Docente"),
        ("active", "Estado"),
    ]
    row_actions = [
        ("Editar", "core:teaching_assignment_update"),
    ]

    def get_queryset(self):
        queryset = TeachingAssignment.objects.select_related(
            "section",
            "section__course",
            "subject",
            "subject__section",
            "teacher",
        )
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(section__name__icontains=query)
            | Q(section__course__name__icontains=query)
            | Q(subject__name__icontains=query)
            | Q(teacher__first_name__icontains=query)
            | Q(teacher__last_name__icontains=query)
        )


class TeachingAssignmentCreateView(AcademicCreateView):
    model = TeachingAssignment
    form_class = TeachingAssignmentForm
    title = "Nueva asignacion docente"
    success_url = reverse_lazy("core:teaching_assignment_list")
    cancel_url_name = "core:teaching_assignment_list"


class TeachingAssignmentUpdateView(AcademicUpdateView):
    model = TeachingAssignment
    form_class = TeachingAssignmentForm
    title = "Editar asignacion docente"
    success_url = reverse_lazy("core:teaching_assignment_list")
    cancel_url_name = "core:teaching_assignment_list"


class UserAccessListView(ManagementAccessMixin, ListView):
    model = User
    template_name = "core/user_access_list.html"
    paginate_by = 30

    def get_queryset(self):
        queryset = User.objects.prefetch_related("groups").order_by("username")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class UserAccessUpdateView(ManagementAccessMixin, UpdateView):
    model = User
    form_class = UserAccessForm
    template_name = "core/academic_form.html"
    title = "Editar acceso de usuario"
    success_url = reverse_lazy("core:user_access_list")
    cancel_url_name = "core:user_access_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class RoleListView(ManagementAccessMixin, ListView):
    model = Group
    template_name = "core/role_list.html"
    paginate_by = 30

    def get_queryset(self):
        queryset = Group.objects.prefetch_related("permissions").order_by("name")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class RoleCreateView(ManagementAccessMixin, CreateView):
    model = Group
    form_class = RoleForm
    template_name = "core/academic_form.html"
    title = "Nuevo rol"
    success_url = reverse_lazy("core:role_list")
    cancel_url_name = "core:role_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class RoleUpdateView(ManagementAccessMixin, UpdateView):
    model = Group
    form_class = RoleForm
    template_name = "core/academic_form.html"
    title = "Editar rol"
    success_url = reverse_lazy("core:role_list")
    cancel_url_name = "core:role_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class MySectionsView(AcademicAccessMixin, ListView):
    template_name = "core/my_sections.html"
    paginate_by = 30

    def get_queryset(self):
        assignments = visible_assignments_for_user(self.request.user)
        section_ids = assignments.values_list("section_id", flat=True).distinct()
        return Section.objects.filter(pk__in=section_ids).select_related("course", "responsible").order_by(
            "course__name",
            "name",
            "-school_year",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Mis secciones"
        return context


class GradeBookView(AcademicAccessMixin, View):
    template_name = "core/gradebook.html"

    def get_assignment(self, assignment_id):
        return get_object_or_404(visible_assignments_for_user(self.request.user), pk=assignment_id)

    def get(self, request, assignment_id):
        assignment = self.get_assignment(assignment_id)
        can_edit = can_edit_grades(request.user)
        subject_competencies = get_subject_competencies(assignment.subject)
        rows = self.get_rows(assignment, create_missing=False)
        return render(
            request,
            self.template_name,
            {
                "assignment": assignment,
                "rows": rows,
                "subject_competencies": subject_competencies,
                "period_fields": GRADE_PERIOD_FIELDS,
                "can_edit_grades": can_edit,
            },
        )

    def post(self, request, assignment_id):
        messages.error(request, "La edicion directa en web esta desactivada. Use la plantilla de Excel para actualizar calificaciones.")
        return redirect("core:gradebook", assignment_id=assignment_id)

    def get_rows(self, assignment, create_missing=False):
        enrollments = Enrollment.objects.filter(
            section=assignment.section,
            active=True,
        ).select_related("student").order_by("student__last_name", "student__first_name")
        rows = []
        for order_number, enrollment in enumerate(enrollments, start=1):
            competency_cells = []
            for subject_competency in get_subject_competencies(assignment.subject):
                if create_missing:
                    grade, _ = Grade.objects.get_or_create(
                        enrollment=enrollment,
                        subject=assignment.subject,
                        subject_competency=subject_competency,
                    )
                else:
                    grade = Grade.objects.filter(
                        enrollment=enrollment,
                        subject=assignment.subject,
                        subject_competency=subject_competency,
                    ).first()
                competency_values = []
                if grade:
                    competency_values = [
                        value
                        for value in (grade.period_1, grade.period_2, grade.period_3, grade.period_4)
                        if value is not None
                    ]
                competency_average = (
                    sum(competency_values) / len(competency_values) if competency_values else None
                )
                competency_cells.append(
                    {
                        "subject_competency": subject_competency,
                        "grade": grade,
                        "average": competency_average,
                    }
                )
            values = []
            period_values = {field_name: [] for field_name in GRADE_PERIOD_FIELDS}
            for competency_cell in competency_cells:
                grade = competency_cell["grade"]
                if grade:
                    for field_name in GRADE_PERIOD_FIELDS:
                        value = getattr(grade, field_name)
                        if value is not None:
                            values.append(value)
                            period_values[field_name].append(value)
            period_averages = [
                sum(period_values[field_name]) / len(period_values[field_name]) if period_values[field_name] else None
                for field_name in GRADE_PERIOD_FIELDS
            ]
            completed_period_averages = [value for value in period_averages if value is not None]
            average = sum(completed_period_averages) / len(completed_period_averages) if completed_period_averages else None
            completion = GradeCompletion.objects.filter(enrollment=enrollment, subject=assignment.subject).first()
            rows.append(
                {
                    "order_number": order_number,
                    "enrollment": enrollment,
                    "competency_cells": competency_cells,
                    "period_averages": period_averages,
                    "average": average,
                    "completion": completion,
                }
            )
        return rows


GRADE_TEMPLATE_VERSION = "1.0"
GRADE_PERIOD_FIELDS = ("period_1", "period_2", "period_3", "period_4")
GRADE_PERIOD_HEADERS = ("p1", "p2", "p3", "p4")
COMPLETION_FIELDS = (
    "cf",
    "cf_50",
    "cef",
    "cef_50",
    "ccf",
    "ccf_30",
    "ceex",
    "ceex_70",
    "cexf",
    "special_cf",
    "special_ce",
)
COMPLETION_TEXT_FIELDS = ("approved", "reproved")
COMPLETION_LABELS = {
    "cf": "CF",
    "cf_50": "50% CF",
    "cef": "CEF",
    "cef_50": "50% CEF",
    "ccf": "CCF",
    "ccf_30": "30% CCF",
    "ceex": "CEEX",
    "ceex_70": "70% CEEX",
    "cexf": "CEXF",
    "special_cf": "CF Esp.",
    "special_ce": "CE Esp.",
    "approved": "A",
    "reproved": "R",
}
COMPLETION_PREVIEW_FIELDS = ("cf", "cef", "ccf", "ceex", "cexf", "special_cf", "special_ce", "approved", "reproved")
DEFAULT_COMPETENCIES = (
    "Comunicativa",
    "Pensamiento logico, creativo y critico / Resolucion de problemas",
    "Etica y ciudadana / Desarrollo personal y espiritual",
    "Cientifica y tecnologica / Ambiental y de la salud",
)


def parse_grade_value(value):
    if value in (None, ""):
        return None
    try:
        grade_value = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError):
        raise ValueError("La nota debe ser numerica.")
    if grade_value < 0 or grade_value > 100:
        raise ValueError("La nota debe estar entre 0 y 100.")
    return grade_value


def parse_text_value(value):
    if value in (None, ""):
        return ""
    return str(value).strip()[:1].upper()


def normalize_header(value):
    return str(value or "").strip().lower()


def find_grade_header(sheet):
    for row_number in range(1, min(sheet.max_row, 30) + 1):
        values = [normalize_header(cell.value) for cell in sheet[row_number]]
        if "inscripcion_id" in values and all(f"c1_{period}" in values for period in GRADE_PERIOD_HEADERS):
            return row_number, {value: index for index, value in enumerate(values)}
    return None, {}


def read_grade_template_metadata(workbook):
    if "_referencia" not in workbook.sheetnames:
        return {}
    sheet = workbook["_referencia"]
    metadata = {}
    for key, value in sheet.iter_rows(min_row=1, max_col=2, values_only=True):
        if key:
            metadata[str(key)] = value
    return metadata


def get_subject_competencies(subject):
    subject_competencies = []
    for description in DEFAULT_COMPETENCIES:
        competency, _ = Competency.objects.get_or_create(description=description)
        subject_competency, _ = SubjectCompetency.objects.get_or_create(subject=subject, competency=competency)
        subject_competencies.append(subject_competency)
    return subject_competencies


class GradeImportView(AcademicAccessMixin, View):
    template_name = "core/grade_import.html"
    session_key = "grade_import_preview"

    def dispatch(self, request, *args, **kwargs):
        if not can_import_grades(request.user):
            messages.error(request, "No tienes permiso para importar calificaciones.")
            return redirect("core:grade_stats")
        return super().dispatch(request, *args, **kwargs)

    def get_assignments(self):
        return visible_assignments_for_user(self.request.user).order_by(
            "section__course__name",
            "section__name",
            "subject__name",
        )

    def get_selected_assignment(self, assignment_id):
        if not assignment_id:
            return None
        return self.get_assignments().filter(pk=assignment_id).first()

    def prepare_form(self, form, selected_assignment=None):
        if selected_assignment:
            form.fields["teaching_assignment"].widget = forms.HiddenInput()
            form.fields["teaching_assignment"].initial = selected_assignment.pk
        return form

    def render_page(self, request, form, preview=None, result=None, selected_assignment=None):
        form = self.prepare_form(form, selected_assignment)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "preview": preview,
                "result": result,
                "selected_assignment": selected_assignment,
            },
        )

    def get(self, request):
        selected_assignment = self.get_selected_assignment(request.GET.get("assignment"))
        initial = {"teaching_assignment": selected_assignment.pk} if selected_assignment else {}
        form = GradeImportForm(assignments=self.get_assignments(), initial=initial)
        request.session.pop(self.session_key, None)
        return self.render_page(request, form, selected_assignment=selected_assignment)

    def post(self, request):
        action = request.POST.get("action", "preview")
        selected_assignment = self.get_selected_assignment(request.POST.get("teaching_assignment"))
        if action == "cancel":
            request.session.pop(self.session_key, None)
            initial = {"teaching_assignment": selected_assignment.pk} if selected_assignment else {}
            form = GradeImportForm(assignments=self.get_assignments(), initial=initial)
            return self.render_page(request, form, selected_assignment=selected_assignment)

        if action == "confirm":
            saved_preview = request.session.get(self.session_key)
            preview_assignment = self.get_selected_assignment(saved_preview.get("assignment_id")) if saved_preview else selected_assignment
            initial = {"teaching_assignment": preview_assignment.pk} if preview_assignment else {}
            form = GradeImportForm(assignments=self.get_assignments(), initial=initial)
            if not saved_preview:
                form.add_error(None, "No hay una vista previa pendiente. Selecciona el archivo nuevamente.")
                return self.render_page(request, form, selected_assignment=preview_assignment)
            assignment = get_object_or_404(self.get_assignments(), pk=saved_preview["assignment_id"])
            result = self.commit_preview(assignment, saved_preview["rows"])
            request.session.pop(self.session_key, None)
            return self.render_page(request, form, result=result, selected_assignment=assignment)

        form = GradeImportForm(request.POST, request.FILES, assignments=self.get_assignments())
        if not form.is_valid():
            return self.render_page(request, form, selected_assignment=selected_assignment)

        assignment = form.cleaned_data["teaching_assignment"]
        preview = self.build_preview(assignment, form.cleaned_data["excel_file"])
        if preview["rows"]:
            request.session[self.session_key] = {
                "assignment_id": assignment.pk,
                "rows": preview["rows"],
            }
            request.session.modified = True
        return self.render_page(request, form, preview=preview, selected_assignment=assignment)

    def clean_decimal_for_session(self, value):
        return str(value) if value is not None else None

    def format_preview_value(self, value):
        return "" if value in (None, "") else str(value)

    def build_completion_summary(self, completion):
        summary = []
        for field_name in COMPLETION_PREVIEW_FIELDS:
            value = self.format_preview_value(completion.get(field_name))
            if value:
                summary.append({"label": COMPLETION_LABELS[field_name], "value": value})
        return summary

    def build_preview(self, assignment, excel_file):
        workbook = load_workbook(excel_file, data_only=True)
        metadata = read_grade_template_metadata(workbook)
        template_assignment_id = metadata.get("assignment_id")
        if template_assignment_id:
            try:
                template_assignment_id = int(template_assignment_id)
            except (TypeError, ValueError):
                template_assignment_id = None
        if template_assignment_id and template_assignment_id != assignment.pk:
            return {
                "rows": [],
                "total": 0,
                "valid": 0,
                "skipped": 0,
                "errors": ["La plantilla cargada no corresponde a la seccion/asignatura seleccionada."],
            }

        sheet = workbook["Calificaciones"] if "Calificaciones" in workbook.sheetnames else workbook.active
        header_row, header_map = find_grade_header(sheet)
        if not header_row:
            return {
                "rows": [],
                "total": 0,
                "valid": 0,
                "skipped": 0,
                "errors": ["No se encontro un encabezado valido de calificaciones en el archivo."],
            }

        enrollment_index = header_map["inscripcion_id"]
        subject_competencies = get_subject_competencies(assignment.subject)
        required_columns = [
            f"c{competency_index}_{period}"
            for competency_index in range(1, len(subject_competencies) + 1)
            for period in GRADE_PERIOD_HEADERS
        ]
        missing_columns = [column for column in required_columns if column not in header_map]
        if missing_columns:
            return {
                "rows": [],
                "total": 0,
                "valid": 0,
                "skipped": 0,
                "errors": ["La plantilla no contiene todas las columnas de competencias requeridas."],
            }
        preview_rows = []
        skipped = 0
        errors = []
        for row_number, row in enumerate(sheet.iter_rows(min_row=header_row + 1, values_only=True), start=header_row + 1):
            enrollment_id = row[enrollment_index] if len(row) > enrollment_index else None
            if not enrollment_id:
                skipped += 1
                continue
            try:
                enrollment = Enrollment.objects.select_related("student").get(pk=enrollment_id, section=assignment.section, active=True)
            except Enrollment.DoesNotExist:
                skipped += 1
                errors.append(f"Fila {row_number}: estudiante no pertenece a esta seccion.")
                continue
            try:
                competencies = []
                for competency_index, subject_competency in enumerate(subject_competencies, start=1):
                    values = {}
                    for field_name, period in zip(GRADE_PERIOD_FIELDS, GRADE_PERIOD_HEADERS):
                        column_index = header_map[f"c{competency_index}_{period}"]
                        raw_value = row[column_index] if len(row) > column_index else None
                        values[field_name] = self.clean_decimal_for_session(parse_grade_value(raw_value))
                    competencies.append(
                        {
                            "subject_competency_id": subject_competency.pk,
                            "label": f"Competencia {competency_index}",
                            "values": values,
                        }
                    )
                completion = {}
                completion_columns = [
                    column for column in (*COMPLETION_FIELDS, *COMPLETION_TEXT_FIELDS) if column in header_map
                ]
                if completion_columns:
                    for field_name in COMPLETION_FIELDS:
                        if field_name in header_map:
                            column_index = header_map[field_name]
                            raw_value = row[column_index] if len(row) > column_index else None
                            completion[field_name] = self.clean_decimal_for_session(parse_grade_value(raw_value))
                    for field_name in COMPLETION_TEXT_FIELDS:
                        if field_name in header_map:
                            column_index = header_map[field_name]
                            raw_value = row[column_index] if len(row) > column_index else None
                            completion[field_name] = parse_text_value(raw_value)
                completion_summary = self.build_completion_summary(completion)
            except ValueError as exc:
                skipped += 1
                errors.append(f"Fila {row_number}: {exc}")
                continue
            preview_rows.append(
                {
                    "row_number": row_number,
                    "enrollment_id": enrollment.pk,
                    "student": str(enrollment.student),
                    "competencies": competencies,
                    "completion": completion,
                    "completion_summary": completion_summary,
                }
            )

        return {
            "rows": preview_rows,
            "total": len(preview_rows) + skipped,
            "valid": len(preview_rows),
            "skipped": skipped,
            "errors": errors[:10],
        }

    def commit_preview(self, assignment, rows):
        updated = 0
        completion_updated = 0
        skipped = 0
        errors = []
        for row in rows:
            try:
                enrollment = Enrollment.objects.get(pk=row["enrollment_id"], section=assignment.section, active=True)
            except Enrollment.DoesNotExist:
                skipped += 1
                continue
            try:
                for competency_row in row["competencies"]:
                    subject_competency = SubjectCompetency.objects.get(
                        pk=competency_row["subject_competency_id"],
                        subject=assignment.subject,
                    )
                    grade, _ = Grade.objects.get_or_create(
                        enrollment=enrollment,
                        subject=assignment.subject,
                        subject_competency=subject_competency,
                    )
                    for field_name in GRADE_PERIOD_FIELDS:
                        setattr(grade, field_name, parse_grade_value(competency_row["values"].get(field_name)))
                    grade.save()

                if row.get("completion"):
                    completion, _ = GradeCompletion.objects.get_or_create(
                        enrollment=enrollment,
                        subject=assignment.subject,
                    )
                    for field_name in COMPLETION_FIELDS:
                        setattr(completion, field_name, parse_grade_value(row["completion"].get(field_name)))
                    for field_name in COMPLETION_TEXT_FIELDS:
                        setattr(completion, field_name, parse_text_value(row["completion"].get(field_name)))
                    completion.save()
                    if row.get("completion_summary"):
                        completion_updated += 1
            except (ValueError, SubjectCompetency.DoesNotExist) as exc:
                skipped += 1
                errors.append(f"{row.get('student', 'Fila desconocida')}: {exc}")
                continue
            updated += 1
        return {"updated": updated, "completion_updated": completion_updated, "skipped": skipped, "errors": errors[:10]}


class GradeTemplateDownloadView(AcademicAccessMixin, View):
    def get(self, request, assignment_id):
        assignment = get_object_or_404(visible_assignments_for_user(request.user), pk=assignment_id)
        subject_competencies = get_subject_competencies(assignment.subject)
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Calificaciones"

        title_fill = PatternFill("solid", fgColor="1F4E78")
        section_fill = PatternFill("solid", fgColor="D9EAF7")
        header_fill = PatternFill("solid", fgColor="305496")
        locked_fill = PatternFill("solid", fgColor="F3F6FA")
        editable_fill = PatternFill("solid", fgColor="FFF2CC")
        border_color = "D9E2F3"
        thin_border = Border(
            left=Side(style="thin", color=border_color),
            right=Side(style="thin", color=border_color),
            top=Side(style="thin", color=border_color),
            bottom=Side(style="thin", color=border_color),
        )

        identity_columns = 4
        periods_per_competency = len(GRADE_PERIOD_HEADERS)
        first_grade_column = identity_columns + 1
        last_grade_column = identity_columns + len(subject_competencies) * periods_per_competency
        first_period_average_column = last_grade_column + 1
        last_period_average_column = first_period_average_column + periods_per_competency - 1
        average_column = last_period_average_column + 1
        status_column = average_column + 1
        first_completion_column = status_column + 1
        completion_column_count = len(COMPLETION_FIELDS) + len(COMPLETION_TEXT_FIELDS)
        last_completion_column = first_completion_column + completion_column_count - 1
        last_column_letter = get_column_letter(last_completion_column)

        sheet.merge_cells(f"A1:{last_column_letter}1")
        sheet["A1"] = "PLANTILLA DE CALIFICACIONES - UNA ASIGNATURA"
        sheet["A1"].fill = title_fill
        sheet["A1"].font = Font(color="FFFFFF", bold=True, size=14)
        sheet["A1"].alignment = Alignment(horizontal="center")

        metadata_rows = [
            ("Curso", str(assignment.section.course), "Seccion", assignment.section.name),
            ("Asignatura", assignment.subject.name, "Docente", str(assignment.teacher)),
            ("Ano escolar", assignment.section.school_year or "", "Fecha de descarga", request.user.get_username()),
        ]
        for row_number, row_values in enumerate(metadata_rows, start=3):
            sheet.append([])
            sheet[f"A{row_number}"], sheet[f"B{row_number}"], sheet[f"D{row_number}"], sheet[f"E{row_number}"] = row_values
            for cell in (sheet[f"A{row_number}"], sheet[f"D{row_number}"]):
                cell.fill = section_fill
                cell.font = Font(bold=True)
            for cell in sheet[row_number]:
                cell.alignment = Alignment(vertical="center")

        sheet.merge_cells(f"A7:{last_column_letter}7")
        sheet["A7"] = "Cada asignatura trabaja 4 competencias. Complete P1, P2, P3 y P4 dentro de cada competencia. Para completivo edite CEF, CEEX, CF Esp. y CE Esp. cuando aplique. Use valores de 0 a 100. No elimine filas ni cambie los encabezados."
        sheet["A7"].fill = PatternFill("solid", fgColor="E2F0D9")
        sheet["A7"].font = Font(color="375623", bold=True)
        sheet["A7"].alignment = Alignment(wrap_text=True)

        group_header_row = 9
        header_row = 10
        technical_header_row = 11
        identity_headers = [
            "inscripcion_id",
            "No.",
            "Apellido(s)",
            "Nombre(s)",
        ]
        visible_headers = identity_headers[:]
        technical_headers = identity_headers[:]
        for index, subject_competency in enumerate(subject_competencies, start=1):
            visible_headers.extend(["P1", "P2", "P3", "P4"])
            technical_headers.extend([f"c{index}_p1", f"c{index}_p2", f"c{index}_p3", f"c{index}_p4"])
        visible_headers.extend(["PC1", "PC2", "PC3", "PC4"])
        technical_headers.extend(["pc1", "pc2", "pc3", "pc4"])
        visible_headers.extend(["Promedio", "Estado"])
        technical_headers.extend(["promedio", "estado"])
        visible_headers.extend(["CF", "50% CF", "CEF", "50% CEF", "CCF", "30% CCF", "CEEX", "70% CEEX", "CEXF", "CF Esp.", "CE Esp.", "A", "R"])
        technical_headers.extend([*COMPLETION_FIELDS, *COMPLETION_TEXT_FIELDS])

        for column_number, value in enumerate(visible_headers, start=1):
            sheet.cell(row=header_row, column=column_number).value = value
        for column_number, value in enumerate(technical_headers, start=1):
            sheet.cell(row=technical_header_row, column=column_number).value = value
        sheet.row_dimensions[technical_header_row].hidden = True

        for column_number, header in enumerate(identity_headers, start=1):
            cell = sheet.cell(row=group_header_row, column=column_number)
            cell.value = header
            cell.fill = header_fill
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            sheet.merge_cells(start_row=group_header_row, start_column=column_number, end_row=header_row, end_column=column_number)

        for competency_index, subject_competency in enumerate(subject_competencies, start=1):
            start_column = first_grade_column + (competency_index - 1) * periods_per_competency
            end_column = start_column + periods_per_competency - 1
            sheet.merge_cells(
                start_row=group_header_row,
                start_column=start_column,
                end_row=group_header_row,
                end_column=end_column,
            )
            cell = sheet.cell(row=group_header_row, column=start_column)
            cell.value = f"Competencia {competency_index}: {subject_competency.competency.description}"
            cell.fill = header_fill
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border

        sheet.merge_cells(
            start_row=group_header_row,
            start_column=first_period_average_column,
            end_row=group_header_row,
            end_column=last_period_average_column,
        )
        cell = sheet.cell(row=group_header_row, column=first_period_average_column)
        cell.value = "Promedio por periodo"
        cell.fill = header_fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

        for column_number, header in ((average_column, "Promedio"), (status_column, "Estado")):
            cell = sheet.cell(row=group_header_row, column=column_number)
            cell.value = header
            cell.fill = header_fill
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            sheet.merge_cells(start_row=group_header_row, start_column=column_number, end_row=header_row, end_column=column_number)

        sheet.merge_cells(
            start_row=group_header_row,
            start_column=first_completion_column,
            end_row=group_header_row,
            end_column=last_completion_column,
        )
        cell = sheet.cell(row=group_header_row, column=first_completion_column)
        cell.value = "Evaluacion completiva"
        cell.fill = header_fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

        for cell in sheet[header_row]:
            if cell.value:
                cell.fill = header_fill
                cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        for cell in sheet[technical_header_row]:
            cell.fill = header_fill
            cell.font = Font(color="FFFFFF", bold=True)
            cell.border = thin_border

        enrollments = Enrollment.objects.filter(section=assignment.section, active=True).select_related("student").order_by(
            "student__last_name",
            "student__first_name",
        )
        first_data_row = technical_header_row + 1
        for order_number, enrollment in enumerate(enrollments, start=1):
            row_number = first_data_row + order_number - 1
            grades_by_competency = {
                grade.subject_competency_id: grade
                for grade in Grade.objects.filter(enrollment=enrollment, subject=assignment.subject)
            }
            row_values = [
                enrollment.pk,
                order_number,
                enrollment.student.last_name,
                enrollment.student.first_name,
            ]
            for subject_competency in subject_competencies:
                grade = grades_by_competency.get(subject_competency.pk)
                row_values.extend(
                    [
                        grade.period_1 if grade else "",
                        grade.period_2 if grade else "",
                        grade.period_3 if grade else "",
                        grade.period_4 if grade else "",
                    ]
                )
            period_average_formulas = []
            for period_offset in range(periods_per_competency):
                period_cells = [
                    f"{get_column_letter(first_grade_column + competency_index * periods_per_competency + period_offset)}{row_number}"
                    for competency_index in range(len(subject_competencies))
                ]
                period_range = ",".join(period_cells)
                period_average_formulas.append(f'=IF(COUNT({period_range})=0,"",ROUND(AVERAGE({period_range}),2))')
            row_values.extend(period_average_formulas)
            row_values.extend(
                [
                    f'=IF(COUNT({get_column_letter(first_period_average_column)}{row_number}:{get_column_letter(last_period_average_column)}{row_number})=0,"",ROUND(AVERAGE({get_column_letter(first_period_average_column)}{row_number}:{get_column_letter(last_period_average_column)}{row_number}),0))',
                    f'=IF(COUNT({get_column_letter(first_grade_column)}{row_number}:{get_column_letter(last_grade_column)}{row_number})=0,"Pendiente",IF(COUNT({get_column_letter(first_grade_column)}{row_number}:{get_column_letter(last_grade_column)}{row_number})={len(subject_competencies) * periods_per_competency},"Completo","Parcial"))',
                ]
            )
            completion = GradeCompletion.objects.filter(enrollment=enrollment, subject=assignment.subject).first()
            cf_col = get_column_letter(first_completion_column)
            cf50_col = get_column_letter(first_completion_column + 1)
            cef_col = get_column_letter(first_completion_column + 2)
            cef50_col = get_column_letter(first_completion_column + 3)
            ccf_col = get_column_letter(first_completion_column + 4)
            ccf30_col = get_column_letter(first_completion_column + 5)
            ceex_col = get_column_letter(first_completion_column + 6)
            ceex70_col = get_column_letter(first_completion_column + 7)
            cexf_col = get_column_letter(first_completion_column + 8)
            special_cf_col = get_column_letter(first_completion_column + 9)
            special_ce_col = get_column_letter(first_completion_column + 10)
            existing_cef = completion.cef if completion else ""
            existing_ceex = completion.ceex if completion else ""
            existing_special_cf = completion.special_cf if completion else ""
            existing_special_ce = completion.special_ce if completion else ""
            row_values.extend(
                [
                    f'=IF({get_column_letter(average_column)}{row_number}="","",ROUND({get_column_letter(average_column)}{row_number},0))',
                    f'=IF({cf_col}{row_number}="","",ROUND({cf_col}{row_number}*0.5,0))',
                    existing_cef,
                    f'=IF({cef_col}{row_number}="","",ROUND({cef_col}{row_number}*0.5,0))',
                    f'=IF({cef_col}{row_number}="","",ROUND(SUM({cf50_col}{row_number},{cef50_col}{row_number}),0))',
                    f'=IF({ccf_col}{row_number}="","",ROUND({ccf_col}{row_number}*0.3,0))',
                    existing_ceex,
                    f'=IF({ceex_col}{row_number}="","",ROUND({ceex_col}{row_number}*0.7,0))',
                    f'=IF({ceex_col}{row_number}="","",ROUND(SUM({ccf30_col}{row_number},{ceex70_col}{row_number}),0))',
                    existing_special_cf,
                    existing_special_ce,
                    f'=IF(MAX({cf_col}{row_number},{ccf_col}{row_number},{cexf_col}{row_number},{special_cf_col}{row_number},{special_ce_col}{row_number})>=70,"A","")',
                    f'=IF(COUNT({cf_col}{row_number},{ccf_col}{row_number},{cexf_col}{row_number},{special_cf_col}{row_number},{special_ce_col}{row_number})=0,"",IF(MAX({cf_col}{row_number},{ccf_col}{row_number},{cexf_col}{row_number},{special_cf_col}{row_number},{special_ce_col}{row_number})>=70,"","R"))',
                ]
            )
            sheet.append(row_values)

        last_data_row = max(sheet.max_row, first_data_row)
        sheet.column_dimensions["A"].hidden = True
        for column_number in range(1, last_completion_column + 1):
            column_letter = get_column_letter(column_number)
            if column_number == 2:
                sheet.column_dimensions[column_letter].width = 8
            elif column_number in (3, 4):
                sheet.column_dimensions[column_letter].width = 26
            elif column_number == status_column:
                sheet.column_dimensions[column_letter].width = 16
            elif first_completion_column <= column_number <= last_completion_column:
                sheet.column_dimensions[column_letter].width = 11
            elif first_grade_column <= column_number <= average_column:
                sheet.column_dimensions[column_letter].width = 10
        sheet.row_dimensions[1].height = 28
        sheet.row_dimensions[7].height = 34
        sheet.row_dimensions[group_header_row].height = 44
        sheet.freeze_panes = f"{get_column_letter(first_grade_column)}{first_data_row}"
        sheet.auto_filter.ref = f"B{header_row}:{last_column_letter}{last_data_row}"

        for row in sheet.iter_rows(min_row=first_data_row, max_row=last_data_row, min_col=1, max_col=last_completion_column):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center", wrap_text=True)
                cell.protection = Protection(locked=True)
                if first_grade_column <= cell.column <= last_grade_column:
                    cell.fill = editable_fill
                    cell.protection = Protection(locked=False)
                    cell.number_format = "0"
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif cell.column == average_column:
                    cell.number_format = "0"
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.fill = locked_fill
                elif first_period_average_column <= cell.column <= last_period_average_column:
                    cell.number_format = "0.00"
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.fill = locked_fill
                elif cell.column in {2, status_column}:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.fill = locked_fill
                elif first_completion_column <= cell.column <= last_completion_column:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.fill = locked_fill
                    if cell.column in {first_completion_column + 11, first_completion_column + 12}:
                        cell.number_format = "@"
                    else:
                        cell.number_format = "0"
                    if cell.column in {first_completion_column + 2, first_completion_column + 6, first_completion_column + 9, first_completion_column + 10}:
                        cell.fill = editable_fill
                        cell.protection = Protection(locked=False)

        validation = DataValidation(
            type="decimal",
            operator="between",
            formula1="0",
            formula2="100",
            allow_blank=True,
        )
        validation.error = "La calificacion debe estar entre 0 y 100."
        validation.errorTitle = "Calificacion invalida"
        validation.prompt = "Digite una calificacion de 0 a 100."
        validation.promptTitle = "Calificacion"
        sheet.add_data_validation(validation)
        validation.add(f"{get_column_letter(first_grade_column)}{first_data_row}:{get_column_letter(last_grade_column)}{last_data_row}")
        validation.add(f"{get_column_letter(first_completion_column + 2)}{first_data_row}:{get_column_letter(first_completion_column + 2)}{last_data_row}")
        validation.add(f"{get_column_letter(first_completion_column + 6)}{first_data_row}:{get_column_letter(first_completion_column + 6)}{last_data_row}")
        validation.add(f"{get_column_letter(first_completion_column + 9)}{first_data_row}:{get_column_letter(first_completion_column + 10)}{last_data_row}")

        for column_number in range(first_grade_column, last_grade_column + 1):
            sheet.cell(row=header_row, column=column_number).comment = Comment(
                "Campo editable por el docente. Valores permitidos: 0 a 100.",
                "SchoolAdmin",
            )
        completion_comments = {
            first_completion_column + 2: "Ingrese CEF cuando el estudiante aplique para evaluacion completiva.",
            first_completion_column + 6: "Ingrese CEEX cuando el estudiante aplique para evaluacion extraordinaria.",
            first_completion_column + 9: "Ingrese CF Esp. si corresponde.",
            first_completion_column + 10: "Ingrese CE Esp. si corresponde.",
        }
        for column_number, comment_text in completion_comments.items():
            sheet.cell(row=header_row, column=column_number).comment = Comment(comment_text, "SchoolAdmin")

        sheet.protection.sheet = True
        sheet.protection.enable()

        reference = workbook.create_sheet("_referencia")
        reference.sheet_state = "hidden"
        reference.append(["format_version", GRADE_TEMPLATE_VERSION])
        reference.append(["assignment_id", assignment.pk])
        reference.append(["section_id", assignment.section_id])
        reference.append(["subject_id", assignment.subject_id])
        reference.append(["course", str(assignment.section.course)])
        reference.append(["section", assignment.section.name])
        reference.append(["subject", assignment.subject.name])
        reference.append(["teacher", str(assignment.teacher)])
        for index, subject_competency in enumerate(subject_competencies, start=1):
            reference.append([f"competency_{index}_id", subject_competency.pk])
            reference.append([f"competency_{index}", subject_competency.competency.description])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        filename = f"calificaciones_{assignment.section}_{assignment.subject.name}.xlsx".replace(" ", "_")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        workbook.save(response)
        return response


class GradeStatsView(AcademicAccessMixin, View):
    template_name = "core/grade_stats.html"

    def dispatch(self, request, *args, **kwargs):
        if not can_view_grade_stats(request.user):
            messages.error(request, "No tienes permiso para ver estadisticas de calificaciones.")
            return redirect("core:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        grades = visible_grades_for_user(request.user)
        context = {
            "grade_count": grades.count(),
            "period_1_avg": grades.aggregate(value=Avg("period_1"))["value"],
            "period_2_avg": grades.aggregate(value=Avg("period_2"))["value"],
            "period_3_avg": grades.aggregate(value=Avg("period_3"))["value"],
            "period_4_avg": grades.aggregate(value=Avg("period_4"))["value"],
            "by_course": grades.values("enrollment__course__name").annotate(total=Count("id"), p1=Avg("period_1")).order_by(
                "enrollment__course__name"
            ),
            "by_section": grades.values("enrollment__section__course__name", "enrollment__section__name").annotate(
                total=Count("id"),
                p1=Avg("period_1"),
            ).order_by("enrollment__section__course__name", "enrollment__section__name"),
            "by_subject": grades.values("subject__name").annotate(total=Count("id"), p1=Avg("period_1")).order_by("subject__name"),
            "by_student": grades.values(
                "enrollment__student__first_name",
                "enrollment__student__last_name",
                "enrollment__student__document_id",
            ).annotate(total=Count("id"), p1=Avg("period_1")).order_by(
                "enrollment__student__last_name",
                "enrollment__student__first_name",
            )[:50],
        }
        return render(request, self.template_name, context)


class RegistryReportView(AcademicAccessMixin, View):
    template_name = "core/registry_report_form.html"

    def get(self, request):
        form = RegistryReportForm()
        return render(request, self.template_name, {"form": form, "title": "Reportes de registro"})

    def post(self, request):
        form = RegistryReportForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "title": "Reportes de registro"})

        section = form.cleaned_data["section"]
        report_type = form.cleaned_data["report_type"]
        scope = form.cleaned_data["scope"]
        student = form.cleaned_data.get("student")
        enrollments = (
            Enrollment.objects.filter(section=section, active=True)
            .select_related("student", "course", "section")
            .order_by("student__last_name", "student__first_name")
        )
        if scope == RegistryReportForm.SCOPE_STUDENT:
            enrollments = enrollments.filter(student=student)

        if report_type == RegistryReportForm.REPORT_FINAL_ACT:
            content = build_final_act_pdf(section)
            filename = f"acta_final_{section.course.name}_{section.name}.pdf"
        elif report_type == RegistryReportForm.REPORT_RCF:
            enrollment = enrollments.first()
            if not enrollment:
                form.add_error(None, "No se encontro una inscripcion activa para ese estudiante en la seccion.")
                return render(request, self.template_name, {"form": form, "title": "Reportes de registro"})
            content = build_rcf_report_pdf(enrollment)
            filename = f"rcf_{enrollment.student.last_name}_{enrollment.student.first_name}.pdf"
        else:
            enrollment_list = list(enrollments)
            if not enrollment_list:
                form.add_error(None, "No hay estudiantes inscritos en esa seleccion.")
                return render(request, self.template_name, {"form": form, "title": "Reportes de registro"})
            content = build_periodic_report_pdf(section, enrollment_list)
            suffix = "individual" if scope == RegistryReportForm.SCOPE_STUDENT else "colectivo"
            filename = f"boletin_periodo_{section.course.name}_{section.name}_{suffix}.pdf"

        response = HttpResponse(content, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename.replace(" ", "_")}"'
        return response


class EquipmentCategoryListView(AdministrationListView):
    model = EquipmentCategory
    title = "Categorias de equipos"
    create_url_name = "core:equipment_category_create"
    edit_url_name = "core:equipment_category_update"
    search_placeholder = "Buscar categoria"
    columns = [("name", "Categoria"), ("active", "Estado")]

    def apply_search(self, queryset, query):
        return queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))


class EquipmentCategoryCreateView(AdministrationCreateView):
    model = EquipmentCategory
    form_class = EquipmentCategoryForm
    title = "Nueva categoria de equipo"
    success_url = reverse_lazy("core:equipment_category_list")
    cancel_url_name = "core:equipment_category_list"


class EquipmentCategoryUpdateView(AdministrationUpdateView):
    model = EquipmentCategory
    form_class = EquipmentCategoryForm
    title = "Editar categoria de equipo"
    success_url = reverse_lazy("core:equipment_category_list")
    cancel_url_name = "core:equipment_category_list"


class EquipmentItemListView(AdministrationListView):
    model = EquipmentItem
    title = "Inventario de equipos"
    create_url_name = "core:equipment_item_create"
    edit_url_name = "core:equipment_item_update"
    search_placeholder = "Buscar por codigo, equipo, marca o ubicacion"
    columns = [
        ("code", "Codigo"),
        ("name", "Equipo"),
        ("category", "Categoria"),
        ("status", "Estado"),
        ("location", "Ubicacion"),
    ]

    def get_queryset(self):
        queryset = EquipmentItem.objects.select_related("category")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(code__icontains=query)
            | Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(model__icontains=query)
            | Q(serial_number__icontains=query)
            | Q(location__icontains=query)
            | Q(category__name__icontains=query)
        )


class EquipmentItemCreateView(AdministrationCreateView):
    model = EquipmentItem
    form_class = EquipmentItemForm
    title = "Nuevo equipo"
    success_url = reverse_lazy("core:equipment_item_list")
    cancel_url_name = "core:equipment_item_list"


class EquipmentItemUpdateView(AdministrationUpdateView):
    model = EquipmentItem
    form_class = EquipmentItemForm
    title = "Editar equipo"
    success_url = reverse_lazy("core:equipment_item_list")
    cancel_url_name = "core:equipment_item_list"


class EquipmentLoanListView(AdministrationListView):
    model = EquipmentLoan
    title = "Prestamos de equipos"
    create_url_name = "core:equipment_loan_create"
    edit_url_name = "core:equipment_loan_update"
    search_placeholder = "Buscar por equipo o persona"
    columns = [
        ("item", "Equipo"),
        ("borrower_name", "Recibido por"),
        ("loan_date", "Prestamo"),
        ("due_date", "Esperado"),
        ("status", "Estado"),
    ]

    def get_queryset(self):
        queryset = EquipmentLoan.objects.select_related("item", "borrowed_by")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(item__name__icontains=query)
            | Q(item__code__icontains=query)
            | Q(borrower_name__icontains=query)
            | Q(borrowed_by__first_name__icontains=query)
            | Q(borrowed_by__last_name__icontains=query)
        )


class EquipmentLoanCreateView(AdministrationCreateView):
    model = EquipmentLoan
    form_class = EquipmentLoanForm
    title = "Nuevo prestamo de equipo"
    success_url = reverse_lazy("core:equipment_loan_list")
    cancel_url_name = "core:equipment_loan_list"


class EquipmentLoanUpdateView(AdministrationUpdateView):
    model = EquipmentLoan
    form_class = EquipmentLoanForm
    title = "Editar prestamo de equipo"
    success_url = reverse_lazy("core:equipment_loan_list")
    cancel_url_name = "core:equipment_loan_list"


class ConsumableItemListView(AdministrationListView):
    model = ConsumableItem
    title = "Material gastable"
    create_url_name = "core:consumable_item_create"
    edit_url_name = "core:consumable_item_update"
    search_placeholder = "Buscar material"
    columns = [
        ("name", "Material"),
        ("category", "Categoria"),
        ("quantity_available", "Existencia"),
        ("unit", "Unidad"),
        ("stock_status", "Estado"),
    ]

    def apply_search(self, queryset, query):
        return queryset.filter(Q(name__icontains=query) | Q(category__icontains=query))


class ConsumableItemCreateView(AdministrationCreateView):
    model = ConsumableItem
    form_class = ConsumableItemForm
    title = "Nuevo material gastable"
    success_url = reverse_lazy("core:consumable_item_list")
    cancel_url_name = "core:consumable_item_list"


class ConsumableItemUpdateView(AdministrationUpdateView):
    model = ConsumableItem
    form_class = ConsumableItemForm
    title = "Editar material gastable"
    success_url = reverse_lazy("core:consumable_item_list")
    cancel_url_name = "core:consumable_item_list"


class ConsumableMovementListView(AdministrationListView):
    model = ConsumableMovement
    title = "Movimientos de material"
    create_url_name = "core:consumable_movement_create"
    edit_url_name = "core:consumable_movement_update"
    search_placeholder = "Buscar por material o destino"
    columns = [
        ("date", "Fecha"),
        ("item", "Material"),
        ("movement_type", "Tipo"),
        ("quantity", "Cantidad"),
        ("delivered_to", "Destino"),
    ]

    def get_queryset(self):
        queryset = ConsumableMovement.objects.select_related("item")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(Q(item__name__icontains=query) | Q(delivered_to__icontains=query) | Q(notes__icontains=query))


class ConsumableMovementCreateView(AdministrationCreateView):
    model = ConsumableMovement
    form_class = ConsumableMovementForm
    title = "Nuevo movimiento de material"
    success_url = reverse_lazy("core:consumable_movement_list")
    cancel_url_name = "core:consumable_movement_list"


class ConsumableMovementUpdateView(AdministrationUpdateView):
    model = ConsumableMovement
    form_class = ConsumableMovementForm
    title = "Editar movimiento de material"
    success_url = reverse_lazy("core:consumable_movement_list")
    cancel_url_name = "core:consumable_movement_list"


class ExpenseListView(AdministrationListView):
    model = Expense
    title = "Gastos"
    create_url_name = "core:expense_create"
    edit_url_name = "core:expense_update"
    search_placeholder = "Buscar gasto, proveedor o categoria"
    columns = [
        ("date", "Fecha"),
        ("category", "Categoria"),
        ("description", "Descripcion"),
        ("vendor", "Proveedor"),
        ("amount", "Monto"),
        ("payment_method", "Pago"),
    ]

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(category__icontains=query)
            | Q(description__icontains=query)
            | Q(vendor__icontains=query)
            | Q(cheque_number__icontains=query)
        )


class ExpenseCreateView(AdministrationCreateView):
    model = Expense
    form_class = ExpenseForm
    title = "Nuevo gasto"
    success_url = reverse_lazy("core:expense_list")
    cancel_url_name = "core:expense_list"


class ExpenseUpdateView(AdministrationUpdateView):
    model = Expense
    form_class = ExpenseForm
    title = "Editar gasto"
    success_url = reverse_lazy("core:expense_list")
    cancel_url_name = "core:expense_list"


class ChequeListView(AdministrationListView):
    model = Cheque
    title = "Cheques"
    create_url_name = "core:cheque_create"
    edit_url_name = "core:cheque_update"
    search_placeholder = "Buscar cheque, beneficiario o concepto"
    columns = [
        ("number", "Numero"),
        ("date", "Fecha"),
        ("payee", "Beneficiario"),
        ("concept", "Concepto"),
        ("amount", "Monto"),
        ("status", "Estado"),
    ]

    def apply_search(self, queryset, query):
        return queryset.filter(Q(number__icontains=query) | Q(payee__icontains=query) | Q(concept__icontains=query))


class ChequeCreateView(AdministrationCreateView):
    model = Cheque
    form_class = ChequeForm
    title = "Nuevo cheque"
    success_url = reverse_lazy("core:cheque_list")
    cancel_url_name = "core:cheque_list"


class ChequeUpdateView(AdministrationUpdateView):
    model = Cheque
    form_class = ChequeForm
    title = "Editar cheque"
    success_url = reverse_lazy("core:cheque_list")
    cancel_url_name = "core:cheque_list"


class BankAccountListView(AdministrationListView):
    model = BankAccount
    title = "Cuentas bancarias"
    create_url_name = "core:bank_account_create"
    edit_url_name = "core:bank_account_update"
    search_placeholder = "Buscar banco o cuenta"
    columns = [
        ("name", "Cuenta"),
        ("bank_name", "Banco"),
        ("account_number", "Numero"),
        ("account_type", "Tipo"),
        ("active", "Estado"),
    ]

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(name__icontains=query) | Q(bank_name__icontains=query) | Q(account_number__icontains=query)
        )


class BankAccountCreateView(AdministrationCreateView):
    model = BankAccount
    form_class = BankAccountForm
    title = "Nueva cuenta bancaria"
    success_url = reverse_lazy("core:bank_account_list")
    cancel_url_name = "core:bank_account_list"


class BankAccountUpdateView(AdministrationUpdateView):
    model = BankAccount
    form_class = BankAccountForm
    title = "Editar cuenta bancaria"
    success_url = reverse_lazy("core:bank_account_list")
    cancel_url_name = "core:bank_account_list"


class BankReconciliationListView(AdministrationListView):
    model = BankReconciliation
    title = "Conciliacion bancaria"
    create_url_name = "core:bank_reconciliation_create"
    edit_url_name = "core:bank_reconciliation_update"
    search_placeholder = "Buscar cuenta o periodo"
    columns = [
        ("period", "Periodo"),
        ("bank_account", "Cuenta"),
        ("statement_balance", "Saldo banco"),
        ("book_balance", "Saldo libro"),
        ("difference", "Diferencia"),
        ("status", "Estado"),
    ]

    def get_queryset(self):
        queryset = BankReconciliation.objects.select_related("bank_account")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(period__icontains=query)
            | Q(bank_account__name__icontains=query)
            | Q(bank_account__bank_name__icontains=query)
            | Q(bank_account__account_number__icontains=query)
        )


class BankReconciliationCreateView(AdministrationCreateView):
    model = BankReconciliation
    form_class = BankReconciliationForm
    title = "Nueva conciliacion bancaria"
    success_url = reverse_lazy("core:bank_reconciliation_list")
    cancel_url_name = "core:bank_reconciliation_list"


class BankReconciliationUpdateView(AdministrationUpdateView):
    model = BankReconciliation
    form_class = BankReconciliationForm
    title = "Editar conciliacion bancaria"
    success_url = reverse_lazy("core:bank_reconciliation_list")
    cancel_url_name = "core:bank_reconciliation_list"


class JournalEntryListView(AdministrationListView):
    model = JournalEntry
    title = "Diario"
    create_url_name = "core:journal_entry_create"
    edit_url_name = "core:journal_entry_update"
    search_placeholder = "Buscar asiento, referencia o cuenta"
    columns = [
        ("date", "Fecha"),
        ("reference", "Referencia"),
        ("description", "Descripcion"),
        ("debit_account", "Debito"),
        ("credit_account", "Credito"),
        ("amount", "Monto"),
    ]

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(reference__icontains=query)
            | Q(description__icontains=query)
            | Q(debit_account__icontains=query)
            | Q(credit_account__icontains=query)
        )


class JournalEntryCreateView(AdministrationCreateView):
    model = JournalEntry
    form_class = JournalEntryForm
    title = "Nuevo asiento de diario"
    success_url = reverse_lazy("core:journal_entry_list")
    cancel_url_name = "core:journal_entry_list"


class JournalEntryUpdateView(AdministrationUpdateView):
    model = JournalEntry
    form_class = JournalEntryForm
    title = "Editar asiento de diario"
    success_url = reverse_lazy("core:journal_entry_list")
    cancel_url_name = "core:journal_entry_list"


class StaffAssignmentListView(AdministrationListView):
    model = StaffAssignment
    title = "Asignaciones de personal"
    create_url_name = "core:staff_assignment_create"
    edit_url_name = "core:staff_assignment_update"
    search_placeholder = "Buscar empleado, area o funcion"
    columns = [
        ("employee", "Empleado"),
        ("area", "Area"),
        ("role", "Funcion"),
        ("start_date", "Desde"),
        ("end_date", "Hasta"),
        ("active", "Estado"),
    ]

    def get_queryset(self):
        queryset = StaffAssignment.objects.select_related("employee")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(employee__first_name__icontains=query)
            | Q(employee__last_name__icontains=query)
            | Q(area__icontains=query)
            | Q(role__icontains=query)
        )


class StaffAssignmentCreateView(AdministrationCreateView):
    model = StaffAssignment
    form_class = StaffAssignmentForm
    title = "Nueva asignacion de personal"
    success_url = reverse_lazy("core:staff_assignment_list")
    cancel_url_name = "core:staff_assignment_list"


class StaffAssignmentUpdateView(AdministrationUpdateView):
    model = StaffAssignment
    form_class = StaffAssignmentForm
    title = "Editar asignacion de personal"
    success_url = reverse_lazy("core:staff_assignment_list")
    cancel_url_name = "core:staff_assignment_list"


class GuidanceCaseListView(GuidanceListView):
    model = GuidanceCase
    title = "Casos de orientacion"
    create_url_name = "core:guidance_case_create"
    edit_url_name = "core:guidance_case_update"
    search_placeholder = "Buscar por caso, estudiante, responsable o descripcion"
    columns = [
        ("case_number", "Caso"),
        ("student", "Estudiante"),
        ("case_type", "Tipo"),
        ("priority", "Prioridad"),
        ("opened_at", "Apertura"),
        ("assigned_to", "Responsable"),
        ("status", "Estado"),
    ]
    row_actions = [
        ("Seguimientos", "core:guidance_followup_list"),
        ("Editar", "core:guidance_case_update"),
    ]

    def get_queryset(self):
        queryset = GuidanceCase.objects.select_related("student", "assigned_to", "referred_by_teacher")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(case_number__icontains=query)
            | Q(student__first_name__icontains=query)
            | Q(student__last_name__icontains=query)
            | Q(student__document_id__icontains=query)
            | Q(assigned_to__first_name__icontains=query)
            | Q(assigned_to__last_name__icontains=query)
            | Q(summary__icontains=query)
            | Q(reported_by__icontains=query)
        )


class GuidanceCaseCreateView(GuidanceCreateView):
    model = GuidanceCase
    form_class = GuidanceCaseForm
    title = "Nuevo caso de orientacion"
    success_url = reverse_lazy("core:guidance_case_list")
    cancel_url_name = "core:guidance_case_list"


class GuidanceCaseUpdateView(GuidanceUpdateView):
    model = GuidanceCase
    form_class = GuidanceCaseForm
    title = "Editar caso de orientacion"
    success_url = reverse_lazy("core:guidance_case_list")
    cancel_url_name = "core:guidance_case_list"


class GuidanceFollowUpListView(GuidanceListView):
    model = GuidanceFollowUp
    title = "Seguimientos de orientacion"
    create_url_name = "core:guidance_followup_create"
    edit_url_name = "core:guidance_followup_update"
    search_placeholder = "Buscar por caso, estudiante, participantes o notas"
    columns = [
        ("date", "Fecha"),
        ("guidance_case", "Caso"),
        ("student", "Estudiante"),
        ("intervention_type", "Tipo"),
        ("attended_by", "Atendido por"),
        ("next_date", "Proxima fecha"),
    ]

    def dispatch(self, request, *args, **kwargs):
        self.guidance_case = None
        case_pk = self.kwargs.get("case_pk")
        if case_pk:
            self.guidance_case = get_object_or_404(GuidanceCase.objects.select_related("student"), pk=case_pk)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = GuidanceFollowUp.objects.select_related("guidance_case", "guidance_case__student", "attended_by")
        if self.guidance_case is not None:
            queryset = queryset.filter(guidance_case=self.guidance_case)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = self.apply_search(queryset, query)
        return queryset

    def apply_search(self, queryset, query):
        return queryset.filter(
            Q(guidance_case__case_number__icontains=query)
            | Q(guidance_case__student__first_name__icontains=query)
            | Q(guidance_case__student__last_name__icontains=query)
            | Q(participants__icontains=query)
            | Q(notes__icontains=query)
            | Q(next_steps__icontains=query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.guidance_case is not None:
            context["title"] = f"Seguimientos - {self.guidance_case.case_number}"
            context["create_url_name"] = "core:guidance_followup_case_create"
            context["create_url_args"] = [self.guidance_case.pk]
        return context


class GuidanceFollowUpCreateView(GuidanceCreateView):
    model = GuidanceFollowUp
    form_class = GuidanceFollowUpForm
    title = "Nuevo seguimiento"
    success_url = reverse_lazy("core:guidance_followup_list")
    cancel_url_name = "core:guidance_followup_list"

    def dispatch(self, request, *args, **kwargs):
        self.guidance_case = None
        case_pk = self.kwargs.get("case_pk")
        if case_pk:
            self.guidance_case = get_object_or_404(GuidanceCase, pk=case_pk)
            self.success_url = reverse_lazy("core:guidance_followup_list", kwargs={"case_pk": self.guidance_case.pk})
            self.cancel_url_name = "core:guidance_followup_list"
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.guidance_case is not None:
            kwargs["guidance_case"] = self.guidance_case
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.guidance_case is not None:
            context["title"] = f"Nuevo seguimiento - {self.guidance_case.case_number}"
            context["cancel_url_name"] = "core:guidance_followup_list"
            context["cancel_url_args"] = [self.guidance_case.pk]
        return context


class GuidanceFollowUpUpdateView(GuidanceUpdateView):
    model = GuidanceFollowUp
    form_class = GuidanceFollowUpForm
    title = "Editar seguimiento"
    success_url = reverse_lazy("core:guidance_followup_list")
    cancel_url_name = "core:guidance_followup_list"


class TeacherListView(PersonListView):
    model = Teacher
    title = "Docentes"
    section_label = "Gestion de docentes"
    create_url_name = "core:teacher_create"
    edit_url_name = "core:teacher_update"
    search_placeholder = "Buscar por nombre, cedula o correo"


class TeacherCreateView(PersonCreateView):
    model = Teacher
    form_class = TeacherForm
    title = "Nuevo docente"
    success_url = reverse_lazy("core:teacher_list")
    cancel_url_name = "core:teacher_list"


class TeacherUpdateView(PersonUpdateView):
    model = Teacher
    form_class = TeacherForm
    title = "Editar docente"
    success_url = reverse_lazy("core:teacher_list")
    cancel_url_name = "core:teacher_list"


class AdministrativeEmployeeListView(PersonListView):
    model = AdministrativeEmployee
    title = "Personal administrativo"
    section_label = "Gestion de personal administrativo"
    create_url_name = "core:employee_create"
    edit_url_name = "core:employee_update"
    search_placeholder = "Buscar por nombre, cedula o correo"


class AdministrativeEmployeeCreateView(PersonCreateView):
    model = AdministrativeEmployee
    form_class = AdministrativeEmployeeForm
    title = "Nuevo empleado administrativo"
    success_url = reverse_lazy("core:employee_list")
    cancel_url_name = "core:employee_list"


class AdministrativeEmployeeUpdateView(PersonUpdateView):
    model = AdministrativeEmployee
    form_class = AdministrativeEmployeeForm
    title = "Editar empleado administrativo"
    success_url = reverse_lazy("core:employee_list")
    cancel_url_name = "core:employee_list"
