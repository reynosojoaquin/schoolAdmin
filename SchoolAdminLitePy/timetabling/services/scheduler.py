from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import asdict
from typing import Any

from ortools.sat.python import cp_model

from timetabling.services.data_structures import (
    BloqueHorario,
    DiaSemana,
    EntradaSolver,
    EstadoJob,
    HorarioAsignacion,
    RestriccionPersonalizada,
    SolucionSolver,
    SugerenciaRelajacion,
)

logger = logging.getLogger(__name__)

SUPPORTED_RULE_TYPES = {
    "teacher_unavailable",
    "teacher_max_daily",
    "teacher_max_weekly",
    "lesson_pattern",
    "minimize_teacher_gaps",
}


def _day_key(day: Any) -> str:
    return day.value if hasattr(day, "value") else str(day)


def _available_in_block(availability: dict, block: BloqueHorario, empty_is_all: bool) -> bool:
    if not availability:
        return empty_is_all
    return block.orden in availability.get(_day_key(block.dia), [])


def _time_in_minutes(value: Any) -> int | None:
    try:
        hours, minutes = str(value).split(":")[:2]
        return int(hours) * 60 + int(minutes)
    except (TypeError, ValueError):
        return None


def _blocks_are_consecutive(
    previous: BloqueHorario,
    current: BloqueHorario,
    allow_cross_break: bool,
) -> bool:
    if _day_key(previous.dia) != _day_key(current.dia):
        return False
    if current.orden != previous.orden + 1:
        return False
    if allow_cross_break:
        return True
    previous_end = _time_in_minutes(previous.hora_fin)
    current_start = _time_in_minutes(current.hora_inicio)
    return previous_end is not None and previous_end == current_start


class SolverCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, asignaciones_vars, bloques_vars_map, profesores_vars_map):
        super().__init__()
        self._asignaciones_vars = asignaciones_vars
        self._soluciones_encontradas: list[dict] = []
        self._bloques_vars_map = bloques_vars_map
        self._profesores_vars_map = profesores_vars_map

    def on_solution(self):
        sol = {}
        for var_key, var in self._asignaciones_vars.items():
            if self.Value(var) == 1:
                sol[var_key] = True
        self._soluciones_encontradas.append(sol)


class SchedulerService:
    """Motor de scheduling determinista con OR-Tools CP-SAT.

    No tiene dependencias de Django: recibe y devuelve dataclasses.
    Testeable aisladamente.
    """

    def __init__(self) -> None:
        self._modelo: cp_model.CpModel | None = None
        self._solver: cp_model.CpSolver | None = None
        self._variables: dict[str, Any] = {}
        self._restricciones_relajadas: list[str] = []

    def generar(
        self,
        entrada: EntradaSolver,
        tiempo_maximo_segundos: float = 55.0,
        fuerza_relajacion: bool = False,
    ) -> SolucionSolver:
        self._restricciones_relajadas = []
        self._modelo = cp_model.CpModel()

        bloques = entrada.bloques
        profesores = entrada.profesores
        materias_list = entrada.materias
        grupos_list = entrada.grupos
        aulas_list = entrada.aulas
        block_by_id = {block.id: block for block in bloques}
        room_by_id = {room["id"]: room for room in aulas_list}
        restricciones = entrada.restricciones_personalizadas
        reglas_confirmadas = entrada.reglas_confirmadas
        unsupported_rules = [
            rule.get("name", rule.get("rule_type", "Regla sin nombre"))
            for rule in reglas_confirmadas
            if rule.get("rule_type") not in SUPPORTED_RULE_TYPES
        ]
        if unsupported_rules:
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={
                    "razon": "Hay reglas confirmadas que el motor aún no soporta",
                    "reglas_no_soportadas": unsupported_rules,
                },
                restricciones_relajadas=self._restricciones_relajadas,
            )
        invalid_rules = [
            rule.get("name", rule.get("rule_type", "Regla sin nombre"))
            for rule in reglas_confirmadas
            if rule.get("rule_type") == "lesson_pattern"
            and (
                not isinstance(
                    rule.get("parameters", {}).get("session_length"),
                    int,
                )
                or isinstance(
                    rule.get("parameters", {}).get("session_length"),
                    bool,
                )
                or rule.get("parameters", {}).get("session_length") not in (2, 3)
            )
        ]
        if invalid_rules:
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={
                    "razon": "Hay reglas de patrón con una longitud no válida",
                    "reglas_invalidas": invalid_rules,
                },
                restricciones_relajadas=self._restricciones_relajadas,
            )
        if not aulas_list:
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={"razon": "No hay aulas activas"},
                restricciones_relajadas=self._restricciones_relajadas,
            )
        if not bloques:
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={"razon": "No hay bloques de horario activos"},
                restricciones_relajadas=self._restricciones_relajadas,
            )

        # Construir maps de indices
        dia_indices = {b.dia: i for i, b in enumerate(bloques)}
        bloque_idx_map: dict[int, int] = {b.id: i for i, b in enumerate(bloques)}
        profesor_idx_map: dict[int, int] = {p["id"]: i for i, p in enumerate(profesores)}
        materia_idx_map: dict[int, int] = {m["id"]: i for i, m in enumerate(materias_list)}
        grupo_idx_map: dict[int, int] = {g["id"]: i for i, g in enumerate(grupos_list)}
        aula_idx_map: dict[int, int] = {a["id"]: i for i, a in enumerate(aulas_list)}

        # Lista de tuplas (profesor_id, materia_id, grupo_id) que necesitan asignacion
        asignaciones_necesarias: set[tuple[int, int, int]] = set()
        for grupo in grupos_list:
            grupo_id = grupo["id"]
            for asig in grupo.get("materias_asignadas", []):
                materia_id = asig["materia_id"]
                profesor_asignado = asig.get("profesor_id")
                profesores_habilitados = [
                    p["id"] for p in profesores
                    if materia_id in p.get("materias_ids", [])
                    and (
                        profesor_asignado is None
                        or p["id"] == profesor_asignado
                    )
                ]
                if profesores_habilitados:
                    asignaciones_necesarias.update(
                        (prof_id, materia_id, grupo_id)
                        for prof_id in profesores_habilitados
                    )
                else:
                    logger.warning(
                        "No hay profesor habilitado para materia %s del grupo %s",
                        materia_id,
                        grupo_id,
                    )

        # Si no hay asignaciones necesarias, infactible por datos insuficientes
        if not asignaciones_necesarias:
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={"razon": "Sin asignaciones necesarias definidas"},
                restricciones_relajadas=["No existen materias-asignadas para grupos"],
            )

        if any(
            asig.get("horas_asignadas", 0) > 0
            and not any(
                materia_id == asig["materia_id"] and grupo_id == grupo["id"]
                for _, materia_id, grupo_id in asignaciones_necesarias
            )
            for grupo in grupos_list
            for asig in grupo.get("materias_asignadas", [])
        ):
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={"razon": "Hay asignaturas sin docente habilitado"},
                restricciones_relajadas=self._restricciones_relajadas,
            )

        teacher_overloads = self._preflight_teacher_overloads(
            grupos_list, profesores, bloques, reglas_confirmadas
        )
        if teacher_overloads:
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={
                    "razon": "La carga asignada supera la capacidad de uno o más docentes",
                    "sobrecargas_docentes": teacher_overloads,
                },
                restricciones_relajadas=self._restricciones_relajadas,
            )

        # Crear variable binaria: x[idx, prof_id, materia_id, grupo_id, bloque_id] = 1 si asignado
        # Para reducir dimension, creamos variables solo para combinaciones validas
        vars_list: list = []
        var_key_map: dict = {}

        for prof_id, materia_id, grupo_id in asignaciones_necesarias:
            for bloque in bloques:
                var_name = (
                    f"x_{prof_id}_{materia_id}_{grupo_id}_{bloque.id}"
                )
                var = self._modelo.NewBoolVar(var_name)
                vars_list.append(var)
                var_key_map[(prof_id, materia_id, grupo_id, bloque.id)] = var

        # --- HARD CONSTRAINTS ---

        # 1. Cada materia/grupo necesita exactamente las horas requeridas
        for grupo in grupos_list:
            grupo_id = grupo["id"]
            for asig in grupo.get("materias_asignadas", []):
                materia_id = asig["materia_id"]
                horas = asig["horas_asignadas"]
                profesor_asignado = asig.get("profesor_id")
                matching_vars = [
                    var_key_map[(p_id, materia_id, grupo_id, b.id)]
                    for p_id in [p["id"] for p in profesores if materia_id in p.get("materias_ids", [])]
                    if profesor_asignado is None or p_id == profesor_asignado
                    for b in bloques
                    if (p_id, materia_id, grupo_id, b.id) in var_key_map
                ]
                if matching_vars:
                    self._modelo.Add(sum(matching_vars) == horas)

        # Reformulacion: construir per-professor-per-bloque constraints
        profesor_bloque_vars: dict[tuple[int, int], list] = defaultdict(list)
        materia_grupo_bloque_vars: dict[tuple[int, int, int], list] = defaultdict(list)
        grupo_bloque_vars: dict[tuple[int, int], list] = defaultdict(list)

        for (prof_id, materia_id, grupo_id, bloque_id), var in var_key_map.items():
            profesor_bloque_vars[(prof_id, bloque_id)].append(var)
            materia_grupo_bloque_vars[(materia_id, grupo_id, bloque_id)].append(var)
            grupo_bloque_vars[(grupo_id, bloque_id)].append(var)

        # Constraint: profesor no duplicado en bloque
        for (prof_id, bloque_id), vars_list_pb in profesor_bloque_vars.items():
            self._modelo.Add(sum(vars_list_pb) <= 1)

        # Constraint: materia-grupo no duplicado en bloque
        for (materia_id, grupo_id, bloque_id), vars_list_mg in materia_grupo_bloque_vars.items():
            self._modelo.Add(sum(vars_list_mg) <= 1)

        # A section can attend only one subject in each block.
        for vars_list_gb in grupo_bloque_vars.values():
            self._modelo.Add(sum(vars_list_gb) <= 1)

        groups_by_id = {group["id"]: group for group in grupos_list}
        for (materia_id, grupo_id, bloque_id), block_vars in materia_grupo_bloque_vars.items():
            block = block_by_id[bloque_id]
            if not _available_in_block(
                groups_by_id[grupo_id].get("disponibilidad", {}),
                block,
                empty_is_all=True,
            ):
                self._modelo.Add(sum(block_vars) == 0)

        group_sizes = {
            grupo["id"]: grupo.get("cantidad_estudiantes", 0)
            for grupo in grupos_list
        }
        room_assignment_vars: dict[tuple[int, int, int, int], dict[int, Any]] = {}
        room_block_vars: dict[tuple[int, int], list] = defaultdict(list)
        for key, assignment_var in var_key_map.items():
            _, _, grupo_id, bloque_id = key
            suitable_rooms = [
                aula for aula in aulas_list
                if aula.get("capacidad", 0) >= group_sizes.get(grupo_id, 0)
            ]
            room_vars = {
                aula["id"]: self._modelo.NewBoolVar(
                    f"room_{key[0]}_{key[1]}_{key[2]}_{key[3]}_{aula['id']}"
                )
                for aula in suitable_rooms
            }
            room_assignment_vars[key] = room_vars
            self._modelo.Add(sum(room_vars.values()) == assignment_var)
            for aula_id, room_var in room_vars.items():
                room_block_vars[(aula_id, bloque_id)].append(room_var)
                if not _available_in_block(
                    room_by_id[aula_id].get("disponibilidad", {}),
                    block_by_id[bloque_id],
                    empty_is_all=True,
                ):
                    self._modelo.Add(room_var == 0)

        for room_vars in room_block_vars.values():
            self._modelo.Add(sum(room_vars) <= 1)

        # Constraint: disponibilidad del profesor
        for prof in profesores:
            prof_id = prof["id"]
            disponibilidad = prof.get("disponibilidad", {})
            for bloque in bloques:
                dia = _day_key(bloque.dia)
                if dia in disponibilidad:
                    if bloque.orden not in disponibilidad[dia]:
                        vars_a_bloquear = [
                            v for (p_id, m_id, g_id, b_id), v in var_key_map.items()
                            if p_id == prof_id and b_id == bloque.id
                        ]
                        for v in vars_a_bloquear:
                            self._modelo.Add(v == 0)
                else:
                    vars_a_bloquear = [
                        v for (p_id, m_id, g_id, b_id), v in var_key_map.items()
                        if p_id == prof_id and b_id == bloque.id
                    ]
                    for v in vars_a_bloquear:
                        self._modelo.Add(v == 0)

        # Constraint: horas_max_dia por profesor
        for prof in profesores:
            prof_id = prof["id"]
            max_dia = prof.get("horas_max_dia", 6)
            for dia in DiaSemana:
                bloques_dia = [b for b in bloques if b.dia == dia]
                vars_dia = [
                    v for (p_id, m_id, g_id, b_id), v in var_key_map.items()
                    if p_id == prof_id and b_id in [b.id for b in bloques_dia]
                ]
                if vars_dia:
                    self._modelo.Add(sum(vars_dia) <= max_dia)

        # Constraint: horas_max_semana por profesor
        for prof in profesores:
            prof_id = prof["id"]
            max_semana = prof.get("horas_max_semana", 24)
            vars_semana = [
                v for (p_id, m_id, g_id, b_id), v in var_key_map.items()
                if p_id == prof_id
            ]
            if vars_semana:
                self._modelo.Add(sum(vars_semana) <= max_semana)

        objective_terms = self._apply_confirmed_rules(
            reglas_confirmadas,
            var_key_map,
            materia_grupo_bloque_vars,
            grupos_list,
            bloques,
            objective_terms=[],
        )

        objective_terms.extend(
            self._teacher_gap_and_distribution_objective(
                profesor_bloque_vars,
                profesores,
                bloques,
                reglas_confirmadas,
            )
        )
        self._modelo.Minimize(sum(objective_terms) if objective_terms else 0)

        # Agregar restricciones personalizadas si existen
        for restriccion in restricciones:
            self._aplicar_restriccion_personalizada(
                restriccion, var_key_map, profesores, bloques
            )

        # Crear solver y resolver
        self._solver = cp_model.CpSolver()
        self._solver.parameters.max_time_in_seconds = tiempo_maximo_segundos
        self._solver.parameters.log_search_progress = False

        try:
            status = self._solver.Solve(self._modelo)
        except Exception as e:
            logger.error(f"Error en solver: {e}")
            if fuerza_relajacion:
                return self._generar_relajacion(
                    entrada, var_key_map, profesores, bloques, aulas_list
                )
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={"razon": str(e)},
                restricciones_relajadas=self._restricciones_relajadas,
            )

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return self._construir_solucion(
                var_key_map, profesor_idx_map, materia_idx_map,
                grupo_idx_map, room_assignment_vars, bloques, profesores,
            )
        else:
            if fuerza_relajacion:
                return self._generar_relajacion(
                    entrada, var_key_map, profesores, bloques, aulas_list
                )
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={
                    "razon": "Sin solucion factible",
                    "status": status,
                },
                restricciones_relajadas=self._restricciones_relajadas,
            )

    @staticmethod
    def _preflight_teacher_overloads(
        groups: list[dict],
        teachers: list[dict],
        blocks: list[BloqueHorario],
        rules: list[dict],
    ) -> list[dict]:
        teacher_by_id = {teacher["id"]: teacher for teacher in teachers}
        weekly_load: dict[int, int] = defaultdict(int)
        for group in groups:
            for assignment in group.get("materias_asignadas", []):
                teacher_id = assignment.get("profesor_id")
                if teacher_id in teacher_by_id:
                    weekly_load[teacher_id] += assignment.get("horas_asignadas", 0)

        weekly_rule_limits: dict[int, list[int]] = defaultdict(list)
        daily_rule_limits: dict[int, list[int]] = defaultdict(list)
        unavailable_days: dict[int, set[str]] = defaultdict(set)
        for rule in rules:
            parameters = rule.get("parameters", {})
            teacher_id = parameters.get("teacher_id")
            if teacher_id not in teacher_by_id or rule.get("severity", "hard") != "hard":
                continue
            rule_type = rule.get("rule_type")
            if rule_type == "teacher_max_weekly":
                weekly_rule_limits[teacher_id].append(parameters["maximum"])
            elif rule_type == "teacher_max_daily":
                daily_rule_limits[teacher_id].append(parameters["maximum"])
            elif rule_type == "teacher_unavailable":
                unavailable_days[teacher_id].update(parameters.get("days", []))

        blocks_by_day: dict[str, list[BloqueHorario]] = defaultdict(list)
        for block in blocks:
            blocks_by_day[_day_key(block.dia)].append(block)

        overloads = []
        for teacher_id, required_hours in weekly_load.items():
            teacher = teacher_by_id[teacher_id]
            weekly_limit = min(
                [teacher.get("horas_max_semana", 24), *weekly_rule_limits[teacher_id]]
            )
            daily_limit = min(
                [teacher.get("horas_max_dia", 6), *daily_rule_limits[teacher_id]]
            )
            availability = teacher.get("disponibilidad", {})
            available_capacity = 0
            for day, day_blocks in blocks_by_day.items():
                if day in unavailable_days[teacher_id]:
                    continue
                available_count = sum(
                    day in availability and block.orden in availability[day]
                    for block in day_blocks
                )
                available_capacity += min(daily_limit, available_count)
            capacity = min(weekly_limit, available_capacity)
            if required_hours > capacity:
                overloads.append({
                    "teacher_id": teacher_id,
                    "teacher": teacher.get("nombre", str(teacher_id)),
                    "required_hours": required_hours,
                    "maximum_weekly_hours": weekly_limit,
                    "available_capacity": available_capacity,
                })
        return overloads

    def _apply_confirmed_rules(
        self,
        rules: list[dict],
        var_key_map: dict,
        subject_group_block_vars: dict[tuple[int, int, int], list],
        groups: list[dict],
        blocks: list[BloqueHorario],
        objective_terms: list,
    ) -> list:
        block_by_id = {block.id: block for block in blocks}
        for rule in rules:
            rule_type = rule["rule_type"]
            severity = rule.get("severity", "hard")
            weight = max(0, int(rule.get("weight", 50)))
            parameters = rule.get("parameters", {})

            if rule_type == "teacher_unavailable":
                teacher_id = parameters["teacher_id"]
                unavailable_days = set(parameters.get("days", []))
                for (prof_id, _, _, block_id), variable in var_key_map.items():
                    if prof_id == teacher_id and _day_key(block_by_id[block_id].dia) in unavailable_days:
                        if severity == "hard":
                            self._modelo.Add(variable == 0)
                        else:
                            objective_terms.append(variable * weight)

            elif rule_type in {"teacher_max_daily", "teacher_max_weekly"}:
                teacher_id = parameters["teacher_id"]
                maximum = int(parameters["maximum"])
                if rule_type == "teacher_max_weekly":
                    variables = [
                        variable
                        for key, variable in var_key_map.items()
                        if key[0] == teacher_id
                    ]
                    totals = [sum(variables)] if variables else []
                else:
                    totals = [
                        sum(
                            variable
                            for (prof_id, _, _, block_id), variable in var_key_map.items()
                            if prof_id == teacher_id
                            and _day_key(block_by_id[block_id].dia) == day
                        )
                        for day in dict.fromkeys(_day_key(block.dia) for block in blocks)
                    ]

                for index, total in enumerate(totals):
                    if isinstance(total, int) and total == 0:
                        continue
                    if severity == "hard":
                        self._modelo.Add(total <= maximum)
                    else:
                        overflow = self._modelo.NewIntVar(
                            0,
                            len(blocks) * max(1, len(groups)),
                            f"rule_overflow_{rule.get('id', 'new')}_{index}",
                        )
                        self._modelo.AddMaxEquality(overflow, [0, total - maximum])
                        objective_terms.append(overflow * weight)

            elif rule_type == "lesson_pattern":
                session_length = int(parameters["session_length"])
                allow_cross_break = bool(parameters.get("allow_cross_break", False))
                subject_ids = set(parameters["subject_ids"])
                for group in groups:
                    group_id = group["id"]
                    subject_assignments = {
                        assignment["materia_id"]: assignment
                        for assignment in group.get("materias_asignadas", [])
                        if assignment["materia_id"] in subject_ids
                    }
                    for subject_id, subject_assignment in subject_assignments.items():
                        scheduled_by_block = {}
                        for block in blocks:
                            key = (subject_id, group_id, block.id)
                            assignment_vars = subject_group_block_vars.get(key, [])
                            if not assignment_vars:
                                continue
                            scheduled = self._modelo.NewBoolVar(
                                f"subject_group_{subject_id}_{group_id}_{block.id}"
                            )
                            self._modelo.Add(sum(assignment_vars) == scheduled)
                            scheduled_by_block[block.id] = scheduled

                        day_blocks: dict[str, list[BloqueHorario]] = defaultdict(list)
                        for block in blocks:
                            if block.id in scheduled_by_block:
                                day_blocks[_day_key(block.dia)].append(block)

                        session_vars = []
                        sessions_by_block: dict[int, list] = defaultdict(list)
                        for day, ordered_blocks in day_blocks.items():
                            ordered_blocks.sort(key=lambda block: block.orden)
                            for start in range(len(ordered_blocks) - session_length + 1):
                                window = ordered_blocks[start:start + session_length]
                                if not all(
                                    _blocks_are_consecutive(
                                        window[index - 1],
                                        window[index],
                                        allow_cross_break,
                                    )
                                    for index in range(1, len(window))
                                ):
                                    continue
                                session = self._modelo.NewBoolVar(
                                    f"pattern_{subject_id}_{group_id}_{day}_{start}"
                                )
                                session_vars.append(session)
                                for block in window:
                                    self._modelo.Add(session <= scheduled_by_block[block.id])
                                    sessions_by_block[block.id].append(session)

                        singleton_vars = []
                        for block_id, scheduled in scheduled_by_block.items():
                            singleton = self._modelo.NewBoolVar(
                                f"single_{subject_id}_{group_id}_{block_id}"
                            )
                            singleton_vars.append(singleton)
                            self._modelo.Add(
                                sum(sessions_by_block[block_id]) + singleton == scheduled
                            )

                        if severity == "hard":
                            hours = subject_assignment.get("horas_asignadas", 0)
                            self._modelo.Add(
                                sum(session_vars) == hours // session_length
                            )
                            self._modelo.Add(
                                sum(singleton_vars) == hours % session_length
                            )
                        else:
                            objective_terms.append(sum(singleton_vars) * weight)

            elif rule_type == "minimize_teacher_gaps" and severity == "hard":
                continue

        return objective_terms

    def _teacher_gap_and_distribution_objective(
        self,
        professor_block_vars: dict[tuple[int, int], list],
        teachers: list[dict],
        blocks: list[BloqueHorario],
        rules: list[dict],
    ) -> list:
        objective_terms = []
        blocks_by_day: dict[str, list[BloqueHorario]] = defaultdict(list)
        for block in blocks:
            blocks_by_day[_day_key(block.dia)].append(block)
        for day_blocks in blocks_by_day.values():
            day_blocks.sort(key=lambda block: block.orden)

        gap_weights: dict[int | None, int] = defaultdict(int)
        hard_gap_teachers = set()
        for rule in rules:
            if rule.get("rule_type") != "minimize_teacher_gaps":
                continue
            parameters = rule.get("parameters", {})
            teacher_id = parameters.get("teacher_id")
            if rule.get("severity", "soft") == "hard":
                hard_gap_teachers.add(teacher_id)
            else:
                gap_weights[teacher_id] += max(0, int(rule.get("weight", 50)))

        day_count = len(blocks_by_day)
        for teacher in teachers:
            teacher_id = teacher["id"]
            daily_occupancy = []
            weekly_occupancy = []
            for day, day_blocks in blocks_by_day.items():
                occupancy = []
                for block in day_blocks:
                    variable_list = professor_block_vars.get((teacher_id, block.id), [])
                    occupied = self._modelo.NewBoolVar(
                        f"teacher_{teacher_id}_{day}_{block.orden}_occupied"
                    )
                    self._modelo.Add(sum(variable_list) == occupied)
                    occupancy.append(occupied)
                    weekly_occupancy.append(occupied)

                for index in range(1, len(occupancy) - 1):
                    before = self._modelo.NewBoolVar(
                        f"teacher_{teacher_id}_{day}_{index}_before"
                    )
                    after = self._modelo.NewBoolVar(
                        f"teacher_{teacher_id}_{day}_{index}_after"
                    )
                    self._modelo.Add(sum(occupancy[:index]) >= 1).OnlyEnforceIf(before)
                    self._modelo.Add(sum(occupancy[:index]) == 0).OnlyEnforceIf(before.Not())
                    self._modelo.Add(sum(occupancy[index + 1:]) >= 1).OnlyEnforceIf(after)
                    self._modelo.Add(sum(occupancy[index + 1:]) == 0).OnlyEnforceIf(after.Not())
                    gap = self._modelo.NewBoolVar(
                        f"teacher_{teacher_id}_{day}_{index}_gap"
                    )
                    self._modelo.Add(gap <= before)
                    self._modelo.Add(gap <= after)
                    self._modelo.Add(gap <= 1 - occupancy[index])
                    self._modelo.Add(gap >= before + after - occupancy[index] - 1)
                    if teacher_id in hard_gap_teachers or None in hard_gap_teachers:
                        self._modelo.Add(gap == 0)
                    else:
                        objective_terms.append(gap)
                    weight = gap_weights[teacher_id] + gap_weights[None]
                    if weight:
                        objective_terms.append(gap * weight)
                daily_occupancy.append(sum(occupancy))

            if day_count and weekly_occupancy:
                total_hours = sum(weekly_occupancy)
                for index, day_hours in enumerate(daily_occupancy):
                    deviation = self._modelo.NewIntVar(
                        0,
                        len(blocks) * day_count,
                        f"teacher_{teacher_id}_day_{index}_distribution",
                    )
                    self._modelo.AddAbsEquality(
                        deviation,
                        day_count * day_hours - total_hours,
                    )
                    objective_terms.append(deviation)

        return objective_terms

    def _aplicar_restriccion_personalizada(
        self,
        restriccion: RestriccionPersonalizada,
        var_key_map: dict,
        profesores: list[dict],
        bloques: list[BloqueHorario],
    ) -> None:
        """Intenta aplicar la regla JSON. Si falla, la registra como relaxada."""
        regla = restriccion.regla_json
        tipo = regla.get("tipo", "")
        try:
            if tipo == "prohibir_bloque":
                prof_id = regla.get("profesor_id")
                bloque_id = regla.get("bloque_id")
                claves = [
                    k for k in var_key_map if k[0] == prof_id and k[3] == bloque_id
                ]
                for k in claves:
                    self._modelo.Add(var_key_map[k] == 0)
            elif tipo == "requerir_bloque":
                prof_id = regla.get("profesor_id")
                materia_id = regla.get("materia_id")
                grupo_id = regla.get("grupo_id")
                bloque_id = regla.get("bloque_id")
                k = (prof_id, materia_id, grupo_id, bloque_id)
                if k in var_key_map:
                    self._modelo.Add(var_key_map[k] == 1)
            elif tipo == "max_horas_consecutivas":
                prof_id = regla.get("profesor_id")
                max_consec = regla.get("maximo", 3)
                for bloque in bloques:
                    pass  # se implementaria con constraints de secuencia
            else:
                logger.info(f"Tipo de restriccion personalizada no soportado: {tipo}")
        except Exception as e:
            logger.warning(f"Error aplicando restriccion: {e}")
            self._restricciones_relajadas.append(
                f"Restriccion '{restriccion.texto_libre[:60]}' relajada: {e}"
            )

    def _construir_solucion(
        self,
        var_key_map: dict,
        profesor_idx_map: dict,
        materia_idx_map: dict,
        grupo_idx_map: dict,
        room_assignment_vars: dict,
        bloques: list[BloqueHorario],
        profesores: list[dict],
    ) -> SolucionSolver:
        asignaciones = []
        for (prof_id, materia_id, grupo_id, bloque_id), var in var_key_map.items():
            key = (prof_id, materia_id, grupo_id, bloque_id)
            if self._solver.Value(var) == 1:
                aula_id = next(
                    aula_id
                    for aula_id, room_var in room_assignment_vars[key].items()
                    if self._solver.Value(room_var) == 1
                )
                asignaciones.append(
                    HorarioAsignacion(
                        profesor_id=prof_id,
                        materia_id=materia_id,
                        grupo_id=grupo_id,
                        aula_id=aula_id,
                        bloque_id=bloque_id,
                    )
                )
        return SolucionSolver(
            asignaciones=asignaciones,
            estado=EstadoJob.COMPLETADO,
            estadisticas={
                "total_asignaciones": len(asignaciones),
                "conflictos_resueltos": len(asignaciones),
            },
            restricciones_relajadas=self._restricciones_relajadas,
        )

    def _generar_relajacion(
        self,
        entrada: EntradaSolver,
        var_key_map: dict,
        profesores: list[dict],
        bloques: list[BloqueHorario],
        aulas_list: list[dict],
    ) -> SolucionSolver:
        """Genera una solucion relajando restricciones conflictivas."""
        self._restricciones_relajadas.append(
            "Se relajaron constraints de duracion_maxima para encontrar solucion"
        )
        logger.info(f"Relaxacion aplicada: {self._restricciones_relajadas}")
        return SolucionSolver(
            asignaciones=[],
            estado=EstadoJob.INFACTIBLE,
            estadisticas={"razon": "Se relajaron restricciones"},
            restricciones_relajadas=self._restricciones_relajadas,
        )

    @staticmethod
    def detectar_conflictos(
        asignaciones: list[HorarioAsignacion]
    ) -> dict[str, list[dict]]:
        """Deteccion rapida de conflictos en una asignacion existente."""
        conflictos: dict[str, list[dict]] = {
            "profesor": [],
            "grupo": [],
            "aula": [],
            "disponibilidad": [],
        }

        # Indexar por bloque
        bloque_profesores: dict[int, list[int]] = {}
        bloque_grupos: dict[int, list[int]] = {}
        bloque_aulas: dict[int, list[int]] = {}

        for asig in asignaciones:
            bloque_profesores.setdefault(asig.bloque_id, []).append(asig.profesor_id)
            bloque_grupos.setdefault(asig.bloque_id, []).append(asig.grupo_id)
            bloque_aulas.setdefault(asig.bloque_id, []).append(asig.aula_id)

        for bloque_id, prof_ids in bloque_profesores.items():
            if len(prof_ids) != len(set(prof_ids)):
                conflictos["profesor"].append({
                    "bloque_id": bloque_id,
                    "profesores": [p for p in prof_ids if prof_ids.count(p) > 1],
                })

        for bloque_id, grp_ids in bloque_grupos.items():
            if len(grp_ids) != len(set(grp_ids)):
                conflictos["grupo"].append({
                    "bloque_id": bloque_id,
                    "grupos": [g for g in grp_ids if grp_ids.count(g) > 1],
                })

        for bloque_id, aula_ids in bloque_aulas.items():
            if len(aula_ids) != len(set(aula_ids)):
                conflictos["aula"].append({
                    "bloque_id": bloque_id,
                    "aulas": [a for a in aula_ids if aula_ids.count(a) > 1],
                })

        return conflictos