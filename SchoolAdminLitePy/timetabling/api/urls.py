from django.urls import path

from timetabling.api import views
from timetabling import views as resource_views

app_name = "timetabling"

urlpatterns = [
    path("recursos/", resource_views.ScheduleResourceListView.as_view(), name="recursos_horario"),
    path(
        "recursos/preparar/",
        resource_views.PrepareScheduleResourcesView.as_view(),
        name="preparar_recursos_horario_ui",
    ),
    path(
        "recursos/bloques/nuevo/",
        resource_views.BloqueHorarioCreateView.as_view(),
        name="bloque_horario_create",
    ),
    path(
        "recursos/bloques/<int:pk>/editar/",
        resource_views.BloqueHorarioUpdateView.as_view(),
        name="bloque_horario_update",
    ),
    path(
        "recursos/bloques/<int:pk>/eliminar/",
        resource_views.BloqueHorarioDeleteView.as_view(),
        name="bloque_horario_delete",
    ),
    path(
        "recursos/aulas/nueva/",
        resource_views.AulaCreateView.as_view(),
        name="aula_create",
    ),
    path(
        "recursos/aulas/<int:pk>/editar/",
        resource_views.AulaUpdateView.as_view(),
        name="aula_update",
    ),
    path(
        "recursos/aulas/<int:pk>/eliminar/",
        resource_views.AulaDeleteView.as_view(),
        name="aula_delete",
    ),
    path(
        "recursos/docentes/<int:pk>/editar/",
        resource_views.ProfesorHorarioUpdateView.as_view(),
        name="profesor_horario_update",
    ),
    path(
        "recursos/secciones/<int:pk>/editar/",
        resource_views.GrupoHorarioUpdateView.as_view(),
        name="grupo_horario_update",
    ),
    path("asistente/", views.asistente_horarios, name="asistente_horarios"),
    path(
        "asistente/reglas/<int:rule_id>/confirmar/",
        views.confirmar_regla_asistente,
        name="confirmar_regla_asistente",
    ),
    path("carga-lectiva.pdf", views.reporte_carga_lectiva, name="reporte_carga_lectiva"),
    path("horarios/generar/", views.generar_horario, name="generar_horario"),
    path(
        "horarios/generar-desde-administracion/",
        views.generar_horario_desde_administracion,
        name="generar_horario_desde_administracion",
    ),
    path(
        "horarios/preparar-recursos/",
        views.preparar_recursos_horario,
        name="preparar_recursos_horario",
    ),
    path("horarios/estado/<str:job_id>/", views.estado_job, name="estado_job"),
    path("horarios/resultado/<str:job_id>/", views.resultado_horario, name="resultado_horario"),
    path("horarios/explicar-conflicto/", views.explicar_conflicto, name="explicar_conflicto"),
    path("horarios/asignacion/<int:asignacion_id>/", views.editar_asignacion, name="editar_asignacion"),
]
