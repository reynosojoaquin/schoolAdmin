from django.contrib import admin

from timetabling.models import Aula, BloqueHorario, Profesor


@admin.register(BloqueHorario)
class BloqueHorarioAdmin(admin.ModelAdmin):
    list_display = ("dia", "orden", "hora_inicio", "hora_fin", "activo")
    list_filter = ("dia", "activo")
    ordering = ("dia", "orden")


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "capacidad", "activa")
    list_filter = ("tipo", "activa")
    search_fields = ("nombre",)


@admin.register(Profesor)
class ProfesorHorarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "docente_administracion", "horas_max_dia", "horas_max_semana")
    search_fields = ("nombre", "docente_administracion__first_name", "docente_administracion__last_name")
    fields = (
        "docente_administracion",
        "nombre",
        "materias_habilitadas",
        "disponibilidad",
        "horas_max_dia",
        "horas_max_semana",
        "activo",
    )
    readonly_fields = (
        "docente_administracion",
        "nombre",
        "materias_habilitadas",
        "activo",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            docente_administracion__isnull=False
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
