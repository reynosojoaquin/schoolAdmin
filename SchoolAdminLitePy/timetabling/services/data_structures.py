from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class DiaSemana(str, Enum):
    LUN = "LUN"
    MAR = "MAR"
    MIÉ = "MIÉ"
    JUE = "JUE"
    VIE = "VIE"


class TipoAula(str, Enum):
    NORMAL = "normal"
    LABORATORIO = "laboratorio"
    AUDITORIO = "auditorio"


class EstadoJob(str, Enum):
    PENDIENTE = "pendiente"
    RESOLVIENDO = "resolviendo"
    COMPLETADO = "completado"
    INFACTIBLE = "infactible"


@dataclass
class BloqueHorario:
    id: int
    dia: DiaSemana
    hora_inicio: str
    hora_fin: str
    orden: int = 0

    def clave_disp(self) -> str:
        return f"{self.dia.value}:{self.hora_inicio}"


@dataclass
class DisponibilidadProfesor:
    dia: DiaSemana
    bloques_inicio: list[int]
    bloques_fin: list[int]

    def contiene_bloque(self, bloque_index: int) -> bool:
        for bi, bf in zip(self.bloques_inicio, self.bloques_fin):
            if bi <= bloque_index < bf:
                return True
        return False


@dataclass
class RestriccionPersonalizada:
    id: Optional[int]
    texto_libre: str
    regla_json: dict[str, Any]


@dataclass
class HorarioAsignacion:
    profesor_id: int
    materia_id: int
    grupo_id: int
    aula_id: int
    bloque_id: int

    def clave_conflicto(self) -> str:
        return f"{self.bloque_id}:{self.profesor_id}:{self.grupo_id}:{self.aula_id}"


@dataclass
class SolucionSolver:
    asignaciones: list[HorarioAsignacion]
    estado: EstadoJob
    estadisticas: dict[str, Any] = field(default_factory=dict)
    restricciones_relajadas: list[str] = field(default_factory=list)


@dataclass
class EntradaSolver:
    bloques: list[BloqueHorario]
    profesores: list[dict[str, Any]]
    materias: list[dict[str, Any]]
    grupos: list[dict[str, Any]]
    aulas: list[dict[str, Any]]
    restricciones_personalizadas: list[RestriccionPersonalizada] = field(default_factory=list)


@dataclass
class SugerenciaRelajacion:
    restriccion: str
    razon: str
    accion_sugerida: str
    impacto_estimado: str