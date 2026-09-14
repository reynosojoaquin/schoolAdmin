import uuid
import logging
from typing import Any

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from timetabling.api.serializers import (
    ExplicarConflictoSerializer,
    GenerarHorarioSerializer,
    ResultadoSerializer,
)
from timetabling.services.data_structures import EstadoJob
from timetabling.models import AsignacionHorario, RestriccionPersonalizada
from timetabling.job_store import guardar_job, obtener_job
from timetabling.services.data_structures import (
    EntradaSolver,
    RestriccionPersonalizada as DataclassRestriccion,
)
from timetabling.services.scheduler import SchedulerService

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def generar_horario(request):
    serializer = GenerarHorarioSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    datos = serializer.validated_data
    job_id = str(uuid.uuid4())

    guardar_job(job_id, {
        "estado": EstadoJob.PENDIENTE,
        "progreso": 0.0,
        "mensaje": "Horario en cola",
        "datos": datos,
    })

    from timetabling.tasks import ejecutar_generacion
    ejecutar_generacion.delay(job_id, datos)

    return Response({"job_id": job_id, "estado": EstadoJob.PENDIENTE}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def estado_job(request, job_id: str):
    job = obtener_job(job_id)
    if not job:
        return Response(
            {"error": "Job no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response({
        "job_id": job["job_id"],
        "estado": job["estado"],
        "progreso": job.get("progreso", 0.0),
        "mensaje": job.get("mensaje", ""),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def resultado_horario(request, job_id: str):
    job = obtener_job(job_id)
    if not job:
        return Response(
            {"error": "Job no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response({
        "job_id": job["job_id"],
        "estado": job["estado"],
        "asignaciones": job.get("asignaciones", []),
        "estadisticas": job.get("estadisticas", {}),
        "restricciones_relajadas": job.get("restricciones_relajadas", []),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
@csrf_exempt
def explicar_conflicto(request):
    serializer = ExplicarConflictoSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    texto = serializer.validated_data["texto_libre"]
    asignaciones = serializer.validated_data.get("asignaciones", [])

    from timetabling.services.reasoning import ConstraintReasoningService
    servicio = ConstraintReasoningService()

    try:
        exlicacion = servicio.explicar_conflicto(texto, asignaciones)
        sugerencias = servicio.sugerir_relajaciones(texto, [])
        return Response({
            "resumen": exlicacion.resumen,
            "conflicto_detectado": exlicacion.conflicto_detectado,
            "sugerencias": [
                {
                    "restriccion": s.restriccion,
                    "razon": s.razon,
                    "accion_sugerida": s.accion_sugerida,
                    "impacto_estimado": s.impacto_estimado,
                }
                for s in sugerencias
            ],
        })
    except ConnectionError as e:
        return Response(
            {"error": f"No se pudo conectar con el servicio de razonamiento: {e}"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        logger.error(f"Error explicando conflicto: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticatedOrReadOnly])
def editar_asignacion(request, asignacion_id: int):
    try:
        asignacion = AsignacionHorario.objects.get(pk=asignacion_id)
    except AsignacionHorario.DoesNotExist:
        return Response(
            {"error": "Asignacion no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = AsignacionHorarioSerializer(
        asignacion, data=request.data, partial=True
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Re-validacion incremental: verificar conflictos
    data = serializer.validated_data
    conflictos = _verificar_conflictos_edit(
        asignacion, data, request.data
    )

    if conflictos:
        return Response(
            {
                "error": "Edicion genera conflictos",
                "conflictos": conflictos,
            },
            status=status.HTTP_409_CONFLICT,
        )

    serializer.save()
    return Response(AsignacionHorarioSerializer(asignacion).data)


def _verificar_conflictos_edit(
    asignacion_original: AsignacionHorario,
    data: dict,
    datos_raw: dict,
) -> list[dict]:
    conflictos = []
    # Verificar que profesor no se duplica en el mismo bloque
    if "bloque_id" in datos_raw and "profesor_id" in datos_raw:
        existentes = AsignacionHorario.objects.filter(
            profesor_id=datos_raw.get("profesor_id", asignacion_original.profesor_id),
            bloque_id=datos_raw.get("bloque_id", asignacion_original.bloque_id),
        ).exclude(pk=asignacion_original.pk)
        if existentes.exists():
            conflictos.append({
                "tipo": "profesor",
                "bloque_id": datos_raw.get("bloque_id"),
                "mensaje": "El profesor ya tiene otra asignacion en este bloque",
            })
    return conflictos