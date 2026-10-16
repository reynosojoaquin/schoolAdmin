from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from apps.core.models import Section, Subject, TeachingAssignment
from timetabling.forms import (
    AulaForm,
    BloqueHorarioForm,
    GrupoHorarioForm,
    ProfesorHorarioForm,
)
from timetabling.models import (
    Aula,
    AsignacionHorario,
    BloqueHorario,
    Grupo,
    Materia,
    Profesor,
)
from timetabling.services.administration_data import (
    ScheduleSetupError,
    get_administration_summary,
    sync_administration_catalogs,
)


class ScheduleManagementAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.has_perm(
            "core.manage_academic_setup"
        )


class ResourceFormContextMixin:
    template_name = "timetabling/resource_form.html"
    cancel_url_name = "timetabling:recursos_horario"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        return context


class ResourceFormSuccessMixin:
    def form_valid(self, form):
        messages.success(self.request, "Recurso guardado correctamente.")
        return super().form_valid(form)


class ScheduleResourceListView(ScheduleManagementAccessMixin, TemplateView):
    template_name = "timetabling/resources.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = get_administration_summary()
        school_year = summary["school_year"]
        current_sections = Section.objects.filter(
            active=True,
            course__active=True,
            school_year=school_year,
        )
        eligible_subjects = Subject.objects.filter(
            section__in=current_sections,
            weekly_hours__gt=0,
        ).select_related("section__course").prefetch_related(
            "teaching_assignments__teacher",
        )
        subjects_without_assignments = []
        active_assignments = TeachingAssignment.objects.filter(
            section__in=current_sections,
            active=True,
            teacher__active=True,
        ).select_related("subject")
        active_subject_ids = {
            assignment.subject_id
            for assignment in active_assignments
            if assignment.subject.weekly_hours > 0
        }
        existing_assignments = {
            assignment.subject_id: assignment
            for assignment in TeachingAssignment.objects.filter(
                section__in=current_sections,
                subject__weekly_hours__gt=0,
            ).select_related("teacher")
        }
        for subject in eligible_subjects:
            if subject.pk in active_subject_ids:
                continue
            subject.existing_teaching_assignment = existing_assignments.get(subject.pk)
            subjects_without_assignments.append(subject)

        current_assignments = TeachingAssignment.objects.filter(
            section__in=current_sections,
            active=True,
            teacher__active=True,
        )
        context.update({
            "summary": summary,
            "subjects_without_assignments": subjects_without_assignments[:20],
            "missing_subject_assignment_count": len(subjects_without_assignments),
            "assignments_on_zero_hour_subjects": current_assignments.filter(
                subject__weekly_hours=0,
            ).count(),
            "blocks": BloqueHorario.objects.annotate(
                assignment_count=Count("asignaciones")
            ),
            "classrooms": Aula.objects.annotate(
                assignment_count=Count("asignaciones")
            ),
            "teacher_profiles": Profesor.objects.filter(
                docente_administracion__active=True,
            ).select_related("docente_administracion").order_by(
                "docente_administracion__last_name",
                "docente_administracion__first_name",
            ),
            "section_profiles": Grupo.objects.filter(
                seccion_administracion__in=current_sections,
            ).select_related(
                "seccion_administracion__course",
            ).order_by(
                "seccion_administracion__course__name",
                "seccion_administracion__name",
            ),
            "unlinked_group_count": Grupo.objects.filter(
                seccion_administracion__isnull=True,
            ).count(),
            "unlinked_teacher_count": Profesor.objects.filter(
                docente_administracion__isnull=True,
            ).count(),
            "unlinked_subject_count": Materia.objects.filter(
                asignatura_administracion__isnull=True,
            ).count(),
        })
        return context


class PrepareScheduleResourcesView(ScheduleManagementAccessMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        try:
            data = sync_administration_catalogs()
        except ScheduleSetupError as error:
            messages.error(request, str(error))
        else:
            messages.success(
                request,
                f"Recursos sincronizados: {len(data['grupos'])} secciones y "
                f"{len(data['profesores'])} docentes.",
            )
        return redirect("timetabling:recursos_horario")


class ResourceDeleteView(ScheduleManagementAccessMixin, DeleteView):
    template_name = "timetabling/resource_confirm_delete.html"
    cancel_url_name = "timetabling:recursos_horario"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if AsignacionHorario.objects.filter(
            **{f"{self.assignment_relation}_id": self.object.pk}
        ).exists():
            messages.error(
                request,
                "No se puede eliminar este recurso porque tiene asignaciones de horario. "
                "Desactívalo para que no se utilice en nuevas generaciones.",
            )
            return redirect(self.success_url)
        messages.success(request, "Recurso eliminado correctamente.")
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["cancel_url_name"] = self.cancel_url_name
        context["related_count"] = AsignacionHorario.objects.filter(
            **{f"{self.assignment_relation}_id": self.object.pk}
        ).count()
        return context


class BloqueHorarioCreateView(
    ScheduleManagementAccessMixin,
    ResourceFormContextMixin,
    ResourceFormSuccessMixin,
    CreateView,
):
    model = BloqueHorario
    form_class = BloqueHorarioForm
    title = "Nuevo bloque horario"
    success_url = reverse_lazy("timetabling:recursos_horario")


class BloqueHorarioUpdateView(
    ScheduleManagementAccessMixin,
    ResourceFormContextMixin,
    ResourceFormSuccessMixin,
    UpdateView,
):
    model = BloqueHorario
    form_class = BloqueHorarioForm
    title = "Editar bloque horario"
    success_url = reverse_lazy("timetabling:recursos_horario")


class BloqueHorarioDeleteView(ResourceDeleteView):
    model = BloqueHorario
    title = "Eliminar bloque horario"
    success_url = reverse_lazy("timetabling:recursos_horario")
    assignment_relation = "bloque"


class AulaCreateView(
    ScheduleManagementAccessMixin,
    ResourceFormContextMixin,
    ResourceFormSuccessMixin,
    CreateView,
):
    model = Aula
    form_class = AulaForm
    title = "Nueva aula"
    success_url = reverse_lazy("timetabling:recursos_horario")


class AulaUpdateView(
    ScheduleManagementAccessMixin,
    ResourceFormContextMixin,
    ResourceFormSuccessMixin,
    UpdateView,
):
    model = Aula
    form_class = AulaForm
    title = "Editar aula"
    success_url = reverse_lazy("timetabling:recursos_horario")


class AulaDeleteView(ResourceDeleteView):
    model = Aula
    title = "Eliminar aula"
    success_url = reverse_lazy("timetabling:recursos_horario")
    assignment_relation = "aula"


class ProfesorHorarioUpdateView(
    ScheduleManagementAccessMixin,
    ResourceFormContextMixin,
    ResourceFormSuccessMixin,
    UpdateView,
):
    model = Profesor
    form_class = ProfesorHorarioForm
    title = "Disponibilidad y carga docente"
    success_url = reverse_lazy("timetabling:recursos_horario")
    queryset = Profesor.objects.filter(
        docente_administracion__isnull=False,
    ).select_related("docente_administracion")


class GrupoHorarioUpdateView(
    ScheduleManagementAccessMixin,
    ResourceFormContextMixin,
    ResourceFormSuccessMixin,
    UpdateView,
):
    model = Grupo
    form_class = GrupoHorarioForm
    title = "Disponibilidad de sección"
    success_url = reverse_lazy("timetabling:recursos_horario")
    queryset = Grupo.objects.filter(
        seccion_administracion__isnull=False,
    ).select_related("seccion_administracion__course")
