import uuid
import logging
from typing import Any

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from apps.core.models import Teacher
from timetabling.api.serializers import (
    ExplicarConflictoSerializer,
    GenerarHorarioSerializer,
    ResultadoSerializer,
)
from timetabling.services.data_structures import EstadoJob
from timetabling.models import (
    AsignacionHorario,
    AssistantConversation,
    AssistantMemory,
    AssistantMemoryRevision,
    AssistantMessage,
    RestriccionPersonalizada,
    SchedulingRule,
)
from timetabling.job_store import guardar_job, obtener_job
from timetabling.services.data_structures import (
    EntradaSolver,
    RestriccionPersonalizada as DataclassRestriccion,
)
from timetabling.services.scheduler import SchedulerService
from timetabling.services.administration_data import (
    ScheduleSetupError,
    get_administration_summary,
    sync_administration_catalogs,
)
from timetabling.report_pdfs import build_teaching_load_pdf, get_teaching_load_data
from timetabling.services.local_assistant import active_memories, request_local_assistant
from timetabling.services.rule_interpreter import create_proposed_rules

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET", "POST"])
def asistente_horarios(request):
    school_year = get_administration_summary()["school_year"]
    conversation = None
    conversation_id = request.POST.get("conversation") or request.GET.get("conversation")
    if conversation_id:
        conversation = AssistantConversation.objects.filter(
            pk=conversation_id,
            user=request.user,
        ).first()

    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        if not prompt:
            messages.error(request, "Escribe una instrucción para el asistente.")
        else:
            if conversation is None:
                conversation = AssistantConversation.objects.create(
                    user=request.user,
                    school_year=school_year,
                    title=prompt[:157] + ("..." if len(prompt) > 157 else ""),
                )
            user_message = AssistantMessage.objects.create(
                conversation=conversation,
                role=AssistantMessage.USER,
                content=prompt,
            )
            if request.POST.get("remember") == "on":
                title = request.POST.get("memory_title", "").strip() or prompt[:160]
                memory = AssistantMemory.objects.create(
                    scope_type=AssistantMemory.SCHOOL_YEAR,
                    school_year=school_year,
                    title=title,
                    content=prompt,
                    status=AssistantMemory.CONFIRMED,
                    source="user",
                    created_by=request.user,
                )
                AssistantMemoryRevision.objects.create(
                    memory=memory,
                    new_data={"title": memory.title, "content": memory.content, "status": memory.status},
                    reason="Memoria confirmada explícitamente desde el asistente.",
                    changed_by=request.user,
                )
            proposed_rules = create_proposed_rules(prompt, school_year, user_message, request.user)
            result = request_local_assistant(prompt, school_year)
            AssistantMessage.objects.create(
                conversation=conversation,
                role=AssistantMessage.ASSISTANT,
                content=result["content"],
                structured_result={
                    "local_model_available": result["available"],
                    "model": result.get("model", ""),
                    "proposed_rule_ids": [rule.pk for rule in proposed_rules],
                },
            )
            return redirect(f"{request.path}?conversation={conversation.pk}")

    conversations = AssistantConversation.objects.filter(user=request.user)[:20]
    if conversation is None:
        conversation = conversations.first()
    return render(
        request,
        "timetabling/assistant.html",
        {
            "school_year": school_year,
            "conversation": conversation,
            "conversations": conversations,
            "assistant_messages": conversation.messages.all() if conversation else [],
            "proposed_rules": SchedulingRule.objects.filter(
                source_message__conversation=conversation,
                status=SchedulingRule.PROPOSED,
            ) if conversation else [],
            "confirmed_rules": SchedulingRule.objects.filter(
                school_year=school_year,
                status=SchedulingRule.CONFIRMED,
                active=True,
            )[:30],
            "memories": active_memories(school_year)[:30],
            "local_ai_configured": bool(settings.LOCAL_AI_URL and settings.LOCAL_AI_MODEL),
        },
    )


@login_required
@require_http_methods(["POST"])
def confirmar_regla_asistente(request, rule_id):
    rule = SchedulingRule.objects.filter(
        pk=rule_id,
        created_by=request.user,
        status=SchedulingRule.PROPOSED,
    ).select_related("source_message__conversation").first()
    if rule is None:
        messages.error(request, "La regla no existe o ya fue procesada.")
        return redirect("timetabling:asistente_horarios")

    action = request.POST.get("action")
    if action == "confirm":
        rule.status = SchedulingRule.CONFIRMED
        rule.confirmed_by = request.user
        rule.confirmed_at = timezone.now()
        rule.save(update_fields=["status", "confirmed_by", "confirmed_at"])
        memory = AssistantMemory.objects.create(
            scope_type=AssistantMemory.SCHOOL_YEAR,
            school_year=rule.school_year,
            category="scheduling_rule",
            title=rule.name,
            content=rule.explanation or rule.name,
            structured_data={
                "rule_id": rule.pk,
                "rule_type": rule.rule_type,
                "severity": rule.severity,
                "weight": rule.weight,
                "parameters": rule.parameters,
            },
            status=AssistantMemory.CONFIRMED,
            source="assistant",
            created_by=request.user,
        )
        AssistantMemoryRevision.objects.create(
            memory=memory,
            new_data=memory.structured_data,
            reason="Regla propuesta por el asistente y confirmada por el usuario.",
            changed_by=request.user,
        )
        messages.success(request, "Regla confirmada y guardada en la memoria persistente.")
    elif action == "reject":
        rule.status = SchedulingRule.REJECTED
        rule.active = False
        rule.save(update_fields=["status", "active"])
        messages.success(request, "Regla rechazada; no será aplicada al horario.")
    else:
        messages.error(request, "Acción no válida.")

    conversation_id = rule.source_message.conversation_id if rule.source_message_id else ""
    return redirect(f"{reverse('timetabling:asistente_horarios')}?conversation={conversation_id}")


def _teacher_filter_context(request, context):
    teachers = list(
        Teacher.objects.filter(
            active=True,
            teaching_assignments__active=True,
            teaching_assignments__section__school_year=context["school_year"],
        )
        .distinct()
        .order_by("last_name", "first_name")
    )
    selected_teacher = None
    try:
        selected_id = int(request.GET.get("teacher", ""))
    except (TypeError, ValueError):
        selected_id = None
    if selected_id:
        selected_teacher = next((teacher for teacher in teachers if teacher.pk == selected_id), None)

    context["teachers"] = teachers
    context["selected_teacher"] = selected_teacher
    if selected_teacher:
        filtered_sections = []
        for section in context["sections"]:
            subjects = [
                subject
                for subject in section["subjects"]
                if subject["teacher_id"] == selected_teacher.pk
            ]
            if subjects:
                filtered_sections.append({**section, "subjects": subjects})
        context["sections"] = filtered_sections
        context["section_count"] = len(filtered_sections)
        context["subject_count"] = sum(len(section["subjects"]) for section in filtered_sections)
        context["total_hours"] = sum(
            subject["weekly_hours"]
            for section in filtered_sections
            for subject in section["subjects"]
        )
        context["teacher_count"] = 1
    return context


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reporte_carga_lectiva(request):
    school_year = get_administration_summary()["school_year"]
    context = _teacher_filter_context(request._request, {"school_year": school_year, "sections": []})
    selected_teacher = context["selected_teacher"]
    report = get_teaching_load_data(school_year, selected_teacher.pk if selected_teacher else None)
    return render(
        request._request,
        "timetabling/carga_lectiva_preview.html",
        {
            "school_year": school_year,
            "selected_teacher": selected_teacher,
            "teachers": context["teachers"],
            "report": report,
        },
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def descargar_carga_lectiva(request):
    school_year = get_administration_summary()["school_year"]
    context = _teacher_filter_context(request._request, {"school_year": school_year, "sections": []})
    selected_teacher = context["selected_teacher"]
    content = build_teaching_load_pdf(school_year, selected_teacher.pk if selected_teacher else None)
    response = HttpResponse(content, content_type="application/pdf")
    suffix = f"_docente_{selected_teacher.pk}" if selected_teacher else ""
    response["Content-Disposition"] = f'attachment; filename="carga_lectiva_{school_year}{suffix}.pdf"'
    return response


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def generar_horario(request):
    if request.method == "GET":
        context = _teacher_filter_context(request._request, get_administration_summary())
        return render(
            request._request,
            "timetabling/generar.html",
            context,
        )

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


@api_view(["POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def generar_horario_desde_administracion(request):
    try:
        datos = sync_administration_catalogs()
    except ScheduleSetupError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    if datos["sobrecargas_docentes"]:
        return Response(
            {
                "error": "Corrige la carga semanal de estos docentes antes de generar.",
                "sobrecargas_docentes": datos["sobrecargas_docentes"],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    job_id = str(uuid.uuid4())
    guardar_job(job_id, {
        "estado": EstadoJob.PENDIENTE,
        "progreso": 0.0,
        "mensaje": "Horario de secciones en cola",
        "datos": datos,
    })

    from timetabling.tasks import ejecutar_generacion
    ejecutar_generacion.delay(job_id, datos)

    return Response(
        {"job_id": job_id, "estado": EstadoJob.PENDIENTE},
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def preparar_recursos_horario(request):
    try:
        datos = sync_administration_catalogs()
    except ScheduleSetupError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        "mensaje": "Perfiles de horario sincronizados. Ya puedes configurar disponibilidades y reglas.",
        "secciones": len(datos["grupos"]),
        "docentes": len(datos["profesores"]),
        "reglas_confirmadas": len(datos["reglas_confirmadas"]),
        "sobrecargas_docentes": datos["sobrecargas_docentes"],
    })


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
        "asignaciones_detalle": job.get("asignaciones_detalle", []),
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
