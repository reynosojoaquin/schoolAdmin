from django.urls import path

from timetabling.api import views

app_name = "timetabling"

urlpatterns = [
    path("horarios/generar/", views.generar_horario, name="generar_horario"),
    path("horarios/estado/<str:job_id>/", views.estado_job, name="estado_job"),
    path("horarios/resultado/<str:job_id>/", views.resultado_horario, name="resultado_horario"),
    path("horarios/explicar-conflicto/", views.explicar_conflicto, name="explicar_conflicto"),
    path("horarios/asignacion/<int:asignacion_id>/", views.editar_asignacion, name="editar_asignacion"),
]