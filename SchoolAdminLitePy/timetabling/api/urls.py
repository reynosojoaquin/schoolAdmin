from django.urls import path

from timetabling.api import views

app_name = "timetabling"

urlpatterns = [
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
    path("horarios/estado/<str:job_id>/", views.estado_job, name="estado_job"),
    path("horarios/resultado/<str:job_id>/", views.resultado_horario, name="resultado_horario"),
    path("horarios/explicar-conflicto/", views.explicar_conflicto, name="explicar_conflicto"),
    path("horarios/asignacion/<int:asignacion_id>/", views.editar_asignacion, name="editar_asignacion"),
]
