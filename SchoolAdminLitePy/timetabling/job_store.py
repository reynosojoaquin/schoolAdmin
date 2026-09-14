from __future__ import annotations

from uuid import UUID

from timetabling.models import HorarioJob


JOB_FIELDS = {
    "estado",
    "progreso",
    "mensaje",
    "datos",
    "asignaciones",
    "estadisticas",
    "restricciones_relajadas",
}


def guardar_job(job_id: str, datos: dict) -> dict:
    defaults = {key: value for key, value in datos.items() if key in JOB_FIELDS}
    job, _ = HorarioJob.objects.update_or_create(job_id=UUID(str(job_id)), defaults=defaults)
    return obtener_job(str(job.job_id)) or {}


def obtener_job(job_id: str) -> dict | None:
    try:
        job = HorarioJob.objects.get(job_id=UUID(str(job_id)))
    except (HorarioJob.DoesNotExist, ValueError):
        return None
    return {
        "job_id": str(job.job_id),
        "estado": job.estado,
        "progreso": job.progreso,
        "mensaje": job.mensaje,
        "datos": job.datos,
        "asignaciones": job.asignaciones,
        "estadisticas": job.estadisticas,
        "restricciones_relajadas": job.restricciones_relajadas,
    }
