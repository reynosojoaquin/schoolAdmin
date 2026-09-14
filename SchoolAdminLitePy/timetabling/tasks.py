from __future__ import annotations

import logging
from dataclasses import asdict

from celery import shared_task

from timetabling.services.data_structures import EstadoJob
from timetabling.services.data_structures import (
    EntradaSolver,
    HorarioAsignacion,
    RestriccionPersonalizada as DataclassRestriccion,
    SolucionSolver,
)
from timetabling.services.scheduler import SchedulerService
from timetabling.models import AsignacionHorario, RestriccionPersonalizada
from timetabling.job_store import guardar_job, obtener_job

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def ejecutar_generacion(self, job_id: str, datos: dict) -> dict:
    try:
        guardar_job(job_id, {
            "estado": EstadoJob.RESOLVIENDO,
            "progreso": 0.3,
            "mensaje": "Ejecutando solver...",
        })

        entrada = EntradaSolver(
            bloques=[
                type("Bloque", (), {
                    "id": b["id"],
                    "dia": b["dia"],
                    "hora_inicio": b["hora_inicio"],
                    "hora_fin": b["hora_fin"],
                    "orden": b.get("orden", 0),
                })
                for b in datos["bloques"]
            ],
            profesores=datos["profesores"],
            materias=datos["materias"],
            grupos=datos["grupos"],
            aulas=datos["aulas"],
            restricciones_personalizadas=[
                DataclassRestriccion(
                    id=r.get("id"),
                    texto_libre=r.get("texto_libre", ""),
                    regla_json=r.get("regla_json", {}),
                )
                for r in datos.get("restricciones_personalizadas", [])
            ],
        )

        servicio = SchedulerService()
        solucion: SolucionSolver = servicio.generar(
            entrada,
            tiempo_maximo_segundos=datos.get("tiempo_maximo_segundos", 55.0),
            fuerza_relajacion=False,
        )

        guardar_job(job_id, {
            "estado": solucion.estado.value,
            "progreso": 1.0,
            "mensaje": "Completado" if solucion.estado.value == EstadoJob.COMPLETADO.value else "Infactible",
            "asignaciones": [
                asdict(asig) for asig in solucion.asignaciones
            ],
            "estadisticas": solucion.estadisticas,
            "restricciones_relajadas": solucion.restricciones_relajadas,
        })

        if solucion.estado.value == EstadoJob.COMPLETADO.value:
            try:
                _guardar_asignaciones_db(solucion.asignaciones)
            except Exception as db_exc:
                logger.warning(f"Error guardando asignaciones en DB: {db_exc}")

        return obtener_job(job_id) or {}

    except Exception as exc:
        logger.error(f"Error en generacion {job_id}: {exc}")
        guardar_job(job_id, {
            "estado": EstadoJob.INFACTIBLE,
            "progreso": 0.0,
            "mensaje": str(exc),
        })
        self.retry(exc=exc)


def _guardar_asignaciones_db(asignaciones: list) -> None:
    for asig in asignaciones:
        AsignacionHorario.objects.create(
            profesor_id=getattr(asig, "profesor_id", 0),
            materia_id=getattr(asig, "materia_id", 0),
            grupo_id=getattr(asig, "grupo_id", 0),
            aula_id=getattr(asig, "aula_id", 0),
            bloque_id=getattr(asig, "bloque_id", 0),
        )
