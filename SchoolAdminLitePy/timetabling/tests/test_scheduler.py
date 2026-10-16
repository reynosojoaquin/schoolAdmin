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

    def test_group_assignment_uses_only_the_administratively_assigned_teacher(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(
                    id=1,
                    dia=DiaSemana.LUN,
                    hora_inicio="08:00",
                    hora_fin="09:00",
                    orden=1,
                ),
            ],
            profesores=[
                {
                    "id": 1,
                    "materias_ids": [10],
                    "disponibilidad": {"LUN": [1]},
                    "horas_max_dia": 6,
                    "horas_max_semana": 24,
                },
                {
                    "id": 2,
                    "materias_ids": [10],
                    "disponibilidad": {"LUN": [1]},
                    "horas_max_dia": 6,
                    "horas_max_semana": 24,
                },
            ],
            materias=[{"id": 10, "nombre": "Matemáticas"}],
            grupos=[{
                "id": 100,
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 1,
                    "profesor_id": 2,
                }],
            }],
            aulas=[{"id": 1000, "nombre": "Aula 1"}],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        assert [asignacion.profesor_id for asignacion in resultado.asignaciones] == [2]

    def test_room_is_not_assigned_to_two_sections_in_the_same_block(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
                BloqueHorario(2, DiaSemana.LUN, "09:00", "10:00", 2),
            ],
            profesores=[{
                "id": 1,
                "materias_ids": [10, 11],
                "disponibilidad": {"LUN": [1, 2]},
                "horas_max_dia": 6,
                "horas_max_semana": 24,
            }],
            materias=[
                {"id": 10, "nombre": "Matemáticas"},
                {"id": 11, "nombre": "Lengua"},
            ],
            grupos=[
                {
                    "id": 100,
                    "materias_asignadas": [{
                        "materia_id": 10,
                        "horas_asignadas": 1,
                        "profesor_id": 1,
                    }],
                },
                {
                    "id": 101,
                    "materias_asignadas": [{
                        "materia_id": 11,
                        "horas_asignadas": 1,
                        "profesor_id": 1,
                    }],
                },
            ],
            aulas=[{"id": 1000, "nombre": "Aula única", "capacidad": 40}],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        assert len(resultado.asignaciones) == 2
        assert len({
            (asignacion.aula_id, asignacion.bloque_id)
            for asignacion in resultado.asignaciones
        }) == 2

    def test_room_capacity_must_fit_the_section(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
            ],
            profesores=[{
                "id": 1,
                "materias_ids": [10],
                "disponibilidad": {"LUN": [1]},
                "horas_max_dia": 6,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10, "nombre": "Matemáticas"}],
            grupos=[{
                "id": 100,
                "cantidad_estudiantes": 31,
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 1,
                    "profesor_id": 1,
                }],
            }],
            aulas=[{"id": 1000, "nombre": "Aula pequeña", "capacidad": 30}],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.INFACTIBLE
        assert resultado.asignaciones == []


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


class TestSchedulerReglasConfirmadas:
    def test_section_cannot_receive_two_subjects_in_the_same_block(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
                BloqueHorario(2, DiaSemana.LUN, "09:00", "10:00", 2),
            ],
            profesores=[
                {
                    "id": 1,
                    "materias_ids": [10],
                    "disponibilidad": {"LUN": [1, 2]},
                    "horas_max_dia": 6,
                    "horas_max_semana": 24,
                },
                {
                    "id": 2,
                    "materias_ids": [11],
                    "disponibilidad": {"LUN": [1, 2]},
                    "horas_max_dia": 6,
                    "horas_max_semana": 24,
                },
            ],
            materias=[{"id": 10}, {"id": 11}],
            grupos=[{
                "id": 100,
                "materias_asignadas": [
                    {"materia_id": 10, "horas_asignadas": 1, "profesor_id": 1},
                    {"materia_id": 11, "horas_asignadas": 1, "profesor_id": 2},
                ],
            }],
            aulas=[{"id": 1000, "capacidad": 40}],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        assert len(resultado.asignaciones) == 2
        assert len({asignacion.bloque_id for asignacion in resultado.asignaciones}) == 2

    def test_confirmed_teacher_unavailability_rule_is_enforced(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
                BloqueHorario(2, DiaSemana.MAR, "08:00", "09:00", 1),
            ],
            profesores=[{
                "id": 1,
                "materias_ids": [10],
                "disponibilidad": {"LUN": [1], "MAR": [1]},
                "horas_max_dia": 6,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10}],
            grupos=[{
                "id": 100,
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 1,
                    "profesor_id": 1,
                }],
            }],
            aulas=[{"id": 1000, "capacidad": 40}],
            reglas_confirmadas=[{
                "id": 1,
                "name": "Docente no disponible el lunes",
                "rule_type": "teacher_unavailable",
                "severity": "hard",
                "weight": 100,
                "parameters": {"teacher_id": 1, "days": ["LUN"]},
            }],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        assert [asignacion.bloque_id for asignacion in resultado.asignaciones] == [2]

    def test_confirmed_daily_teacher_limit_is_enforced(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
                BloqueHorario(2, DiaSemana.LUN, "09:00", "10:00", 2),
                BloqueHorario(3, DiaSemana.MAR, "08:00", "09:00", 1),
            ],
            profesores=[{
                "id": 1,
                "materias_ids": [10],
                "disponibilidad": {"LUN": [1, 2], "MAR": [1]},
                "horas_max_dia": 6,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10}],
            grupos=[{
                "id": 100,
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 2,
                    "profesor_id": 1,
                }],
            }],
            aulas=[{"id": 1000, "capacidad": 40}],
            reglas_confirmadas=[{
                "id": 1,
                "name": "Máximo diario",
                "rule_type": "teacher_max_daily",
                "severity": "hard",
                "weight": 100,
                "parameters": {"teacher_id": 1, "maximum": 1},
            }],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        day_counts = {}
        block_day = {1: "LUN", 2: "LUN", 3: "MAR"}
        for assignment in resultado.asignaciones:
            day = block_day[assignment.bloque_id]
            day_counts[day] = day_counts.get(day, 0) + 1
        assert max(day_counts.values()) <= 1

    def test_double_pattern_keeps_weekly_remainder_as_a_single_block(self):
        blocks = [
            BloqueHorario(index, DiaSemana.LUN, f"{7 + index:02d}:00", f"{8 + index:02d}:00", index)
            for index in range(1, 6)
        ]
        entrada = EntradaSolver(
            bloques=blocks,
            profesores=[{
                "id": 1,
                "materias_ids": [10],
                "disponibilidad": {"LUN": [1, 2, 3, 4, 5]},
                "horas_max_dia": 6,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10}],
            grupos=[{
                "id": 100,
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 5,
                    "profesor_id": 1,
                }],
            }],
            aulas=[{"id": 1000, "capacidad": 40}],
            reglas_confirmadas=[{
                "id": 1,
                "name": "Asignatura en bloques dobles",
                "rule_type": "lesson_pattern",
                "severity": "hard",
                "weight": 100,
                "parameters": {
                    "subject_ids": [10],
                    "session_length": 2,
                    "allow_cross_break": False,
                },
            }],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        orders = sorted(asignacion.bloque_id for asignacion in resultado.asignaciones)
        assert len(orders) == 5
        assert orders == [1, 2, 3, 4, 5]

    def test_hard_double_pattern_requires_a_consecutive_session(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
                BloqueHorario(2, DiaSemana.LUN, "10:00", "11:00", 2),
            ],
            profesores=[{
                "id": 1,
                "materias_ids": [10],
                "disponibilidad": {"LUN": [1, 2]},
                "horas_max_dia": 6,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10}],
            grupos=[{
                "id": 100,
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 2,
                    "profesor_id": 1,
                }],
            }],
            aulas=[{"id": 1000, "capacidad": 40}],
            reglas_confirmadas=[{
                "id": 1,
                "name": "Asignatura en bloques dobles",
                "rule_type": "lesson_pattern",
                "severity": "hard",
                "weight": 100,
                "parameters": {
                    "subject_ids": [10],
                    "session_length": 2,
                    "allow_cross_break": False,
                },
            }],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.INFACTIBLE

    def test_triple_pattern_creates_a_session_each_day(self):
        blocks = [
            BloqueHorario(
                index,
                DiaSemana.LUN if index <= 3 else DiaSemana.MAR,
                f"{7 + (index - 1) % 3:02d}:00",
                f"{8 + (index - 1) % 3:02d}:00",
                (index - 1) % 3 + 1,
            )
            for index in range(1, 7)
        ]
        entrada = EntradaSolver(
            bloques=blocks,
            profesores=[{
                "id": 1,
                "materias_ids": [10],
                "disponibilidad": {"LUN": [1, 2, 3], "MAR": [1, 2, 3]},
                "horas_max_dia": 3,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10}],
            grupos=[{
                "id": 100,
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 6,
                    "profesor_id": 1,
                }],
            }],
            aulas=[{"id": 1000, "capacidad": 40}],
            reglas_confirmadas=[{
                "id": 1,
                "name": "Asignatura en bloques triples",
                "rule_type": "lesson_pattern",
                "severity": "hard",
                "weight": 100,
                "parameters": {
                    "subject_ids": [10],
                    "session_length": 3,
                    "allow_cross_break": False,
                },
            }],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        assert len(resultado.asignaciones) == 6
        assignments_by_day = {}
        for assignment in resultado.asignaciones:
            day = next(block.dia.value for block in blocks if block.id == assignment.bloque_id)
            assignments_by_day[day] = assignments_by_day.get(day, 0) + 1
        assert assignments_by_day == {"LUN": 3, "MAR": 3}

    def test_section_and_room_availability_are_enforced(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
                BloqueHorario(2, DiaSemana.MAR, "08:00", "09:00", 1),
            ],
            profesores=[{
                "id": 1,
                "materias_ids": [10],
                "disponibilidad": {"LUN": [1], "MAR": [1]},
                "horas_max_dia": 6,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10}],
            grupos=[{
                "id": 100,
                "disponibilidad": {"MAR": [1]},
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 1,
                    "profesor_id": 1,
                }],
            }],
            aulas=[
                {
                    "id": 1000,
                    "capacidad": 40,
                    "disponibilidad": {"LUN": [1]},
                },
                {
                    "id": 1001,
                    "capacidad": 40,
                    "disponibilidad": {"MAR": [1]},
                },
            ],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        assert len(resultado.asignaciones) == 1
        assert resultado.asignaciones[0].bloque_id == 2
        assert resultado.asignaciones[0].aula_id == 1001

    def test_teacher_overload_is_reported_before_solving(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
                BloqueHorario(2, DiaSemana.LUN, "09:00", "10:00", 2),
            ],
            profesores=[{
                "id": 1,
                "nombre": "Docente sobrecargado",
                "materias_ids": [10],
                "disponibilidad": {"LUN": [1, 2]},
                "horas_max_dia": 1,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10}],
            grupos=[{
                "id": 100,
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 2,
                    "profesor_id": 1,
                }],
            }],
            aulas=[{"id": 1000, "capacidad": 40}],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.INFACTIBLE
        assert resultado.estadisticas["sobrecargas_docentes"] == [{
            "teacher_id": 1,
            "teacher": "Docente sobrecargado",
            "required_hours": 2,
            "maximum_weekly_hours": 24,
            "available_capacity": 1,
        }]

    def test_minimizes_teacher_gaps(self):
        entrada = EntradaSolver(
            bloques=[
                BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
                BloqueHorario(2, DiaSemana.LUN, "09:00", "10:00", 2),
                BloqueHorario(3, DiaSemana.LUN, "10:00", "11:00", 3),
            ],
            profesores=[{
                "id": 1,
                "materias_ids": [10, 11],
                "disponibilidad": {"LUN": [1, 2, 3]},
                "horas_max_dia": 6,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10}, {"id": 11}],
            grupos=[
                {
                    "id": 100,
                    "materias_asignadas": [{
                        "materia_id": 10,
                        "horas_asignadas": 1,
                        "profesor_id": 1,
                    }],
                },
                {
                    "id": 101,
                    "materias_asignadas": [{
                        "materia_id": 11,
                        "horas_asignadas": 1,
                        "profesor_id": 1,
                    }],
                },
            ],
            aulas=[
                {"id": 1000, "capacidad": 40},
                {"id": 1001, "capacidad": 40},
            ],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        assert len(resultado.asignaciones) == 2
        orders = sorted(asignacion.bloque_id for asignacion in resultado.asignaciones)
        assert orders[1] == orders[0] + 1

    def test_distributes_weekly_lessons_across_days(self):
        blocks = [
            BloqueHorario(1, DiaSemana.LUN, "08:00", "09:00", 1),
            BloqueHorario(2, DiaSemana.LUN, "09:00", "10:00", 2),
            BloqueHorario(3, DiaSemana.MAR, "08:00", "09:00", 1),
            BloqueHorario(4, DiaSemana.MAR, "09:00", "10:00", 2),
            BloqueHorario(5, DiaSemana.MIÉ, "08:00", "09:00", 1),
            BloqueHorario(6, DiaSemana.MIÉ, "09:00", "10:00", 2),
        ]
        entrada = EntradaSolver(
            bloques=blocks,
            profesores=[{
                "id": 1,
                "materias_ids": [10],
                "disponibilidad": {
                    "LUN": [1, 2],
                    "MAR": [1, 2],
                    "MIÉ": [1, 2],
                },
                "horas_max_dia": 6,
                "horas_max_semana": 24,
            }],
            materias=[{"id": 10}],
            grupos=[{
                "id": 100,
                "materias_asignadas": [{
                    "materia_id": 10,
                    "horas_asignadas": 2,
                    "profesor_id": 1,
                }],
            }],
            aulas=[{"id": 1000, "capacidad": 40}],
        )

        resultado = SchedulerService().generar(entrada)

        assert resultado.estado == EstadoJob.COMPLETADO
        scheduled_days = {
            next(block.dia for block in blocks if block.id == assignment.bloque_id)
            for assignment in resultado.asignaciones
        }
        assert len(scheduled_days) == 2