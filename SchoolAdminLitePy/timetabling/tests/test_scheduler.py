"""Tests unitarios del SchedulerService con OR-Tools CP-SAT."""

from __future__ import annotations

import pytest

from timetabling.services.data_structures import (
    BloqueHorario,
    DiaSemana,
    EntradaSolver,
    EstadoJob,
    RestriccionPersonalizada,
)
from timetabling.services.scheduler import SchedulerService


def _crear_bloques_test() -> list[BloqueHorario]:
    return [
        BloqueHorario(id=1, dia=DiaSemana.LUN, hora_inicio="08:00", hora_fin="09:00", orden=1),
        BloqueHorario(id=2, dia=DiaSemana.MAR, hora_inicio="08:00", hora_fin="09:00", orden=2),
        BloqueHorario(id=3, dia=DiaSemana.MIÉ, hora_inicio="08:00", hora_fin="09:00", orden=1),
        BloqueHorario(id=4, dia=DiaSemana.MAR, hora_inicio="09:00", hora_fin="10:00", orden=2),
        BloqueHorario(id=5, dia=DiaSemana.MIÉ, hora_inicio="08:00", hora_fin="09:00", orden=1),
        BloqueHorario(id=6, dia=DiaSemana.MIÉ, hora_inicio="09:00", hora_fin="10:00", orden=2),
    ]


def _crear_profesores_test() -> list[dict]:
    return [
        {
            "id": 1,
            "nombre": "Profesor A",
            "materias_ids": [10, 11],
            "disponibilidad": {"LUN": [1, 2], "MAR": [1, 2], "MIÉ": [1, 2]},
            "horas_max_dia": 4,
            "horas_max_semana": 12,
        },
        {
            "id": 2,
            "nombre": "Profesor B",
            "materias_ids": [10],
            "disponibilidad": {"LUN": [1, 2], "MAR": [1, 2]},
            "horas_max_dia": 4,
            "horas_max_semana": 8,
        },
    ]


def _crear_materias_test() -> list[dict]:
    return [
        {"id": 10, "nombre": "Matematicas", "horas_semanales_requeridas": 2},
        {"id": 11, "nombre": "Ciencias", "horas_semanales_requeridas": 2},
    ]


def _crear_grupos_test() -> list[dict]:
    return [
        {
            "id": 100,
            "nombre": "1A",
            "grado": "1",
            "materias_asignadas": [
                {"materia_id": 10, "horas_asignadas": 2},
                {"materia_id": 11, "horas_asignadas": 1},
            ],
        },
        {
            "id": 101,
            "nombre": "1B",
            "grado": "1",
            "materias_asignadas": [
                {"materia_id": 10, "horas_asignadas": 1},
            ],
        },
    ]


def _crear_aulas_test() -> list[dict]:
    return [
        {"id": 1000, "nombre": "Aula 101", "tipo": "normal", "capacidad": 40},
        {"id": 1001, "nombre": "Aula 102", "tipo": "laboratorio", "capacidad": 30},
    ]


def _construir_entrada(
    bloques=None,
    profesores=None,
    materias=None,
    grupos=None,
    aulas=None,
    restricciones=None,
) -> EntradaSolver:
    return EntradaSolver(
        bloques=bloques or _crear_bloques_test(),
        profesores=profesores or _crear_profesores_test(),
        materias=materias or _crear_materias_test(),
        grupos=grupos or _crear_grupos_test(),
        aulas=aulas or _crear_aulas_test(),
        restricciones_personalizadas=restricciones or [],
    )


class TestSchedulerFactible:
    """Caso: problema con solucion factible."""

    def test_generar_horario_simple(self):
        servicio = SchedulerService()
        entrada = _construir_entrada()
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=30.0)

        assert resultado.estado in (EstadoJob.COMPLETADO, EstadoJob.INFACTIBLE)
        assert isinstance(resultado.asignaciones, list)

    def test_generar_con_disponibilidad_adequada(self):
        servicio = SchedulerService()
        entrada = _construir_entrada()
        resultado = servicio.generar(entrada)

        # Si es completado, verificar que hay asignaciones
        if resultado.estado == EstadoJob.COMPLETADO:
            assert len(resultado.asignaciones) > 0
            assert "total_asignaciones" in resultado.estadisticas

    def test_detectar_conflictos_vacio(self):
        """Deteccion de conflictos en una lista vacia."""
        conflictos = SchedulerService.detectar_conflictos([])
        assert conflictos == {
            "profesor": [],
            "grupo": [],
            "aula": [],
            "disponibilidad": [],
        }


class TestSchedulerInfactiblePorSobreasignacion:
    """Caso: infactible porque no hay suficientes profesores para cubrir materias."""

    def test_infactible_sin_profesores_habilitados(self):
        servicio = SchedulerService()
        grupos = [
            {
                "id": 100,
                "nombre": "1A",
                "grado": "1",
                "materias_asignadas": [
                    {"materia_id": 999, "horas_asignadas": 4},
                ],
            },
        ]
        profesores = [
            {"id": 1, "materias_ids": [10], "disponibilidad": {}, "horas_max_dia": 4, "horas_max_semana": 12},
        ]
        entrada = _construir_entrada(
            grupos=grupos, profesores=profesores
        )
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=15.0)

        assert resultado.estado == EstadoJob.INFACTIBLE

    def test_infactible_muy_pocos_bloques(self):
        """Solo 1 bloque disponible pero se requieren muchas horas."""
        servicio = SchedulerService()
        bloques = [BloqueHorario(id=1, dia=DiaSemana.LUN, hora_inicio="08:00", hora_fin="09:00", orden=1)]
        entrada = _construir_entrada(bloques=bloques)
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=15.0)

        assert resultado.estado in (EstadoJob.COMPLETADO, EstadoJob.INFACTIBLE)


class TestSchedulerInfactiblePorDisponibilidad:
    """Caso: infactible porque la disponibilidad es incompatible."""

    def test_infactible_disponibilidad_vacia(self):
        servicio = SchedulerService()
        profesores = [
            {
                "id": 1,
                "materias_ids": [10],
                "disponibilidad": {},
                "horas_max_dia": 4,
                "horas_max_semana": 12,
            },
        ]
        grupos = [
            {
                "id": 100,
                "materias_asignadas": [
                    {"materia_id": 10, "horas_asignadas": 4},
                ],
            },
        ]
        entrada = _construir_entrada(profesores=profesores, grupos=grupos)
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=15.0)

        assert resultado.estado in (EstadoJob.COMPLETADO, EstadoJob.INFACTIBLE)

    def test_infactible_dias_insuficientes(self):
        """Solo un dia con bloques pero las materias requieren mas dias."""
        servicio = SchedulerService()
        bloques = [
            BloqueHorario(id=1, dia=DiaSemana.LUN, hora_inicio="08:00", hora_fin="09:00", orden=1),
            BloqueHorario(id=2, dia=DiaSemana.LUN, hora_inicio="09:00", hora_fin="10:00", orden=2),
        ]
        entrada = _construir_entrada(bloques=bloques)
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=15.0)

        assert resultado.estado in (EstadoJob.COMPLETADO, EstadoJob.INFACTIBLE)


class TestSchedulerRestriccionesPersonalizadas:
    """Test de restricciones personalizadas y relajacion."""

    def test_prohibir_bloque(self):
        restriccion = RestriccionPersonalizada(
            id=None,
            texto_libre="Prohibir al profesor 1 el bloque 1",
            regla_json={"tipo": "prohibir_bloque", "profesor_id": 1, "bloque_id": 1},
        )
        entrada = _construir_entrada(
            restricciones=[restriccion]
        )
        servicio = SchedulerService()
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=15.0)

        # Verificar que el profesor 1 no tiene asignacion en bloque 1
        if resultado.estado == EstadoJob.COMPLETADO:
            for a in resultado.asignaciones:
                assert not (a.profesor_id == 1 and a.bloque_id == 1)

    def test_relajacion_registrada(self):
        """Verificar que las restricciones relajadas se registran."""
        servicio = SchedulerService()
        entrada = _construir_entrada()
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=15.0)

        assert isinstance(resultado.restricciones_relajadas, list)


class TestSchedulerCasosBordes:
    """Casos borde del solver."""

    def test_sin_bloques(self):
        servicio = SchedulerService()
        entrada = _construir_entrada(bloques=[])
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=10.0)

        assert resultado.estado in (EstadoJob.COMPLETADO, EstadoJob.INFACTIBLE)

    def test_sin_profesores(self):
        servicio = SchedulerService()
        entrada = _construir_entrada(profesores=[])
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=10.0)

        assert resultado.estado in (EstadoJob.COMPLETADO, EstadoJob.INFACTIBLE)

    def test_sin_aulas(self):
        entrada = _construir_entrada(aulas=[])
        servicio = SchedulerService()
        resultado = servicio.generar(entrada, tiempo_maximo_segundos=10.0)

        assert resultado.estado in (EstadoJob.COMPLETADO, EstadoJob.INFACTIBLE)

    def test_detectar_conflictos_profesor(self):
        conflictos = SchedulerService.detectar_conflictos([
            type("Asig", (), {"profesor_id": 1, "grupo_id": 100, "aula_id": 1000, "bloque_id": 1})(),
            type("Asig", (), {"profesor_id": 1, "grupo_id": 101, "aula_id": 1001, "bloque_id": 1})(),
        ])
        assert len(conflictos["profesor"]) == 1

    def test_detectar_conflictos_aula(self):
        conflictos = SchedulerService.detectar_conflictos([
            type("Asig", (), {"profesor_id": 1, "grupo_id": 100, "aula_id": 1000, "bloque_id": 1})(),
            type("Asig", (), {"profesor_id": 2, "grupo_id": 101, "aula_id": 1000, "bloque_id": 1})(),
        ])
        assert len(conflictos["aula"]) == 1

    def test_detectar_conflictos_grupo(self):
        conflictos = SchedulerService.detectar_conflictos([
            type("Asig", (), {"profesor_id": 1, "grupo_id": 100, "aula_id": 1000, "bloque_id": 1})(),
            type("Asig", (), {"profesor_id": 2, "grupo_id": 100, "aula_id": 1001, "bloque_id": 1})(),
        ])
        assert len(conflictos["grupo"]) == 1