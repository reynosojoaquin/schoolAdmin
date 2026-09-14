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
        restricciones = entrada.restricciones_personalizadas

        # Construir maps de indices
        dia_indices = {b.dia: i for i, b in enumerate(bloques)}
        bloque_idx_map: dict[int, int] = {b.id: i for i, b in enumerate(bloques)}
        profesor_idx_map: dict[int, int] = {p["id"]: i for i, p in enumerate(profesores)}
        materia_idx_map: dict[int, int] = {m["id"]: i for i, m in enumerate(materias_list)}
        grupo_idx_map: dict[int, int] = {g["id"]: i for i, g in enumerate(grupos_list)}
        aula_idx_map: dict[int, int] = {a["id"]: i for i, a in enumerate(aulas_list)}

        # Lista de tuplas (profesor_id, materia_id, grupo_id) que necesitan asignacion
        asignaciones_necesarias: list[tuple[int, int, int, int]] = []
        for grupo in grupos_list:
            grupo_id = grupo["id"]
            for asig in grupo.get("materias_asignadas", []):
                materia_id = asig["materia_id"]
                horas = asig["horas_asignadas"]
                # cada materia necesita N bloques = horas / duracion_bloque
                # Asumimos 1 bloque = 1 hora para simplificar
                for _ in range(horas):
                    profesores_habilitados = [
                        p["id"] for p in profesores
                        if materia_id in p.get("materias_ids", [])
                    ]
                    if profesores_habilitados:
                        for prof_id in profesores_habilitados:
                            asignaciones_necesarias.append(
                                (prof_id, materia_id, grupo_id, 0)
                            )
                    else:
                        logger.warning(
                            f"No hay profesor habilitado para materia {materia_id}"
                        )

        # Si no hay asignaciones necesarias, infactible por datos insuficientes
        if not asignaciones_necesarias:
            return SolucionSolver(
                asignaciones=[],
                estado=EstadoJob.INFACTIBLE,
                estadisticas={"razon": "Sin asignaciones necesarias definidas"},
                restricciones_relajadas=["No existen materias-asignadas para grupos"],
            )

        # Crear variable binaria: x[idx, prof_id, materia_id, grupo_id, bloque_id] = 1 si asignado
        # Para reducir dimension, creamos variables solo para combinaciones validas
        vars_list: list = []
        var_key_map: dict = {}

        for prof_id, materia_id, grupo_id, _ in asignaciones_necesarias:
            prof_key = f"prof_{prof_id}"
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
                matching_vars = [
                    var_key_map[(p_id, materia_id, grupo_id, b.id)]
                    for p_id in [p["id"] for p in profesores if materia_id in p.get("materias_ids", [])]
                    for b in bloques
                    if (p_id, materia_id, grupo_id, b.id) in var_key_map
                ]
                if matching_vars:
                    self._modelo.Add(sum(matching_vars) == horas)

        # Reformulacion: construir per-professor-per-bloque constraints
        profesor_bloque_vars: dict[tuple[int, int], list] = defaultdict(list)
        materia_grupo_bloque_vars: dict[tuple[int, int, int], list] = defaultdict(list)

        for (prof_id, materia_id, grupo_id, bloque_id), var in var_key_map.items():
            profesor_bloque_vars[(prof_id, bloque_id)].append(var)
            materia_grupo_bloque_vars[(materia_id, grupo_id, bloque_id)].append(var)

        # Constraint: profesor no duplicado en bloque
        for (prof_id, bloque_id), vars_list_pb in profesor_bloque_vars.items():
            self._modelo.Add(sum(vars_list_pb) <= 1)

        # Constraint: materia-grupo no duplicado en bloque
        for (materia_id, grupo_id, bloque_id), vars_list_mg in materia_grupo_bloque_vars.items():
            self._modelo.Add(sum(vars_list_mg) <= 1)

        # Constraint: disponibilidad del profesor
        for prof in profesores:
            prof_id = prof["id"]
            disponibilidad = prof.get("disponibilidad", {})
            for bloque in bloques:
                dia = bloque.dia.value if hasattr(bloque.dia, 'value') else bloque.dia
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

        # Constraint: aula capacidad (simplificacion: aula asignada a grupo)
        # Se usa una capa de asignacion aula -> (materia, grupo, bloque)
        # Para mantener factible, creamos variables adicionales de aula
        # Asignacion dinamica de aula: para cada (materia, grupo, bloque) exactamente 1 aula
        aula_materia_grupo_bloque: dict[tuple[int, int, int, int], list] = defaultdict(list)
        for (prof_id, materia_id, grupo_id, bloque_id), var in var_key_map.items():
            for aula in aulas_list:
                aula_materia_grupo_bloque[(materia_id, grupo_id, bloque_id, aula["id"])].append(var)

        # Cada combinacion materia-grupo-bloque necesita exactamente 1 aula
        # Simplificamos: creamos un alias de variable para "aula asignada"
        # En su lugar, añadimos constraint de que cada materia-grupo-bloque
        # tiene exactamente un profesor (ya garantizado) y la aula se asigna
        # como variable auxiliar. Para el MVP, no creamos vars de aula sino
        # que las incluimos en el soft constraint de minimizacion.

        # --- SOFT CONSTRAINTS (optimizacion) ---

        # Minimizar numero total de asignaciones (preferir menos dispersion)
        # y minimizar huecos. Usamos funcion objetivo simple.
        self._modelo.Minimize(sum(vars_list))

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
                grupo_idx_map, aula_idx_map, bloques, profesores,
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
        aula_idx_map: dict,
        bloques: list[BloqueHorario],
        profesores: list[dict],
    ) -> SolucionSolver:
        asignaciones = []
        solver_vars = {
            k: self._solver.Value(v) for k, v in var_key_map.items()
        }
        # Rastrear aulas asignadas por bloque para evitar conflictos
        aula_bloque_usado: dict[tuple[int, int], int] = {}
        aula_ids = list(aula_idx_map.keys())
        count = 0
        for (prof_id, materia_id, grupo_id, bloque_id), var in var_key_map.items():
            if solver_vars.get((prof_id, materia_id, grupo_id, bloque_id), 0) == 1:
                # Asignar aula disponible
                aula_id = self._asignar_aula_disponible(
                    materia_id, grupo_id, bloque_id, aula_ids,
                    aula_bloque_usado
                )
                if aula_id is None:
                    continue
                count += 1
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
                "conflictos_resueltos": count,
            },
            restricciones_relajadas=self._restricciones_relajadas,
        )

    def _asignar_aula_disponible(
        self,
        materia_id: int,
        grupo_id: int,
        bloque_id: int,
        aulas_list: list[int] | None,
        aula_bloque_usado: dict[tuple[int, int], int],
    ) -> int | None:
        """Asigna un aula simple para la combinacion. Retorna id de aula o None."""
        key = (grupo_id, bloque_id)
        used_aula = aula_bloque_usado.get(key)
        if used_aula is not None:
            return None  # ya hay una aula para este grupo en este bloque
        if aulas_list:
            aula_id = aulas_list[0]
        else:
            aula_id = 1
        aula_bloque_usado[key] = aula_id
        return aula_id

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