from django.contrib import admin

from timetabling.models import (
    AssistantConversation,
    AssistantMemory,
    AssistantMessage,
    Aula,
    BloqueHorario,
    Profesor,
    SchedulingRule,
)


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


@admin.register(AssistantMemory)
class AssistantMemoryAdmin(admin.ModelAdmin):
    list_display = ("title", "scope_type", "school_year", "status", "active", "priority")
    list_filter = ("scope_type", "school_year", "status", "active")
    search_fields = ("title", "content")
    readonly_fields = ("created_at", "updated_at", "last_used_at", "use_count")


class AssistantMessageInline(admin.TabularInline):
    model = AssistantMessage
    extra = 0
    readonly_fields = ("role", "content", "structured_result", "created_at")
    can_delete = False


@admin.register(AssistantConversation)
class AssistantConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "school_year", "active", "updated_at")
    list_filter = ("school_year", "active")
    search_fields = ("title", "user__username")
    readonly_fields = ("created_at", "updated_at")
    inlines = (AssistantMessageInline,)


@admin.register(SchedulingRule)
class SchedulingRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "school_year", "rule_type", "severity", "status", "active")
    list_filter = ("school_year", "rule_type", "severity", "status", "active")
    search_fields = ("name", "explanation")
    readonly_fields = ("created_at", "confirmed_at")
