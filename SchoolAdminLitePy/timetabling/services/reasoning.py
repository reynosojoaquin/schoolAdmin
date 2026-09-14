from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

import httpx

from timetabling.services.data_structures import SugerenciaRelajacion

logger = logging.getLogger(__name__)


@dataclass
class ExplicacionConflicto:
    resumen: str
    conflicto_detectado: str
    sugerencias: list[SugerenciaRelajacion]
    restricciones_relajadas: list[str]


class ConstraintReasoningService:
    """Capa de razonamiento via Ollama/llama.cpp (modelo 7-8B).

    Solo se invoca en endpoints de lenguaje natural, nunca en el hot path del solver.
    """

    def __init__(self, base_url: str = "http://localhost:11434", modelo: str = "llama3") -> None:
        self.base_url = base_url.rstrip("/")
        self.modelo = modelo

    def _chat(
        self,
        mensajes: list[dict[str, str]],
        timeout: int = 30,
    ) -> str:
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.modelo,
                        "messages": mensajes,
                        "stream": False,
                        "options": {"temperature": 0.3},
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Error llamando Ollama: {e}")
            raise ConnectionError(f"No se pudo conectar con Ollama: {e}")

    def parsear_restricciones(
        self, texto: str
    ) -> dict[str, Any]:
        """Parsea restricciones en lenguaje natural -> JSON estructurado."""
        prompt = self._construir_prompt_parseo(texto)
        contenido = self._chat([{"role": "user", "content": prompt}])
        try:
            inicio = contenido.find("{")
            fin = contenido.rfind("}") + 1
            if inicio != -1 and fin != 0:
                return json.loads(contenido[inicio:fin])
            return json.loads(contenido)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"No se pudo parsear JSON de Ollama: {e}")
            return {"texto_original": texto, "raw": contenido, "parseo_valido": False}

    def explicar_conflicto(
        self,
        texto_conflicto: str,
        asignaciones: list[dict] | None = None,
        restricciones_relajadas: list[str] | None = None,
    ) -> ExplicacionConflicto:
        """Genera explicacion en lenguaje natural de por que el solver fallo."""
        mensajes = [
            {"role": "system", "content": (
                "Eres un experto en scheduling escolar. Explica en lenguaje natural "
                "por que un solver de horarios falló y sugiere relajaciones de restricciones. "
                "Responde siempre en español."
            )},
            {"role": "user", "content": self._construir_prompt_explicar(
                texto_conflicto,
                asignaciones,
                restricciones_relajadas,
            )},
        ]
        contenido = self._chat(mensajes)
        return self._parsear_respuesta_conflicto(contenido)

    def sugerir_relajaciones(
        self,
        conflicto: str,
        restricciones_existentes: list[dict],
    ) -> list[SugerenciaRelajacion]:
        """Sugiere 2-3 relajaciones cuando no hay solucion factible."""
        prompt = self._construir_prompt_relajacion(conflicto, restricciones_existentes)
        contenido = self._chat([{"role": "user", "content": prompt}])

        sugerencias = self._parsear_sugerencias(contenido)
        if not sugerencias:
            sugerencias = [
                SugerenciaRelajacion(
                    restriccion="horas_max_dia",
                    razon="El solver no encontro solucion respetando el maximo de horas diarias",
                    accion_sugerida="Aumentar horas_max_dia en 1-2 horas para el profesor afectado",
                    impacto_estimado="Bajo - puede generar mas carga laboral",
                ),
                SugerenciaRelajacion(
                    restriccion="disponibilidad",
                    razon="La disponibilidad declarada es demasiado restrictiva",
                    accion_sugerida="Ampliar la ventana de disponibilidad en los dias conflictivos",
                    impacto_estimado="Medio - requiere ajustar agenda del profesor",
                ),
            ]
        return sugerencias[:3]

    def _parsear_respuesta_conflicto(
        self, contenido: str
    ) -> ExplicacionConflicto:
        return ExplicacionConflicto(
            resumen=contenido[:200],
            conflicto_detectado=contenido,
            sugerencias=[],
            restricciones_relajadas=[],
        )

    def _parsear_sugerencias(
        self, contenido: str
    ) -> list[SugerenciaRelajacion]:
        sugerencias: list[SugerenciaRelajacion] = []
        try:
            inicio = contenido.find("[")
            fin = contenido.rfind("]") + 1
            if inicio != -1 and fin != 0:
                datos = json.loads(contenido[inicio:fin])
                for d in datos:
                    sugerencias.append(SugerenciaRelajacion(
                        restriccion=d.get("restriccion", ""),
                        razon=d.get("razon", ""),
                        accion_sugerida=d.get("accion_sugerida", ""),
                        impacto_estimado=d.get("impacto_estimado", ""),
                    ))
        except (json.JSONDecodeError, TypeError):
            pass
        return sugerencias

    def _construir_prompt_parseo(self, texto: str) -> str:
        return (
            "Parsea el siguiente texto sobre restricciones de horario escolar "
            "y devuelve UN SOLO objeto JSON válido con la estructura:\n\n"
            '{"tipo": "prohibir_bloque | requerir_bloque | max_horas_consecutivas | dia_libre", '
            '"profesor_id": "opcional", "materia_id": "opcional", "grupo_id": "opcional", '
            '"bloque_id": "opcional", "valor": "opcional", "descripcion": "texto"}\n\n'
            f"TEXTO: {texto}\n\nResponde SOLO con el JSON, sin markdown ni texto extra."
        )

    def _construir_prompt_explicar(
        self,
        texto_conflicto: str,
        asignaciones: list[dict] | None,
        restricciones_relajadas: list[str] | None,
    ) -> str:
        return (
            "El solver de horarios escolares fallo con la siguiente informacion:\n\n"
            f"CONFLICTO: {texto_conflicto}\n\n"
            f"RESTRICCIONES RELAJADAS: {restricciones_relajadas or []}\n\n"
            "Responde en español explicando:\n"
            "1. Por qué ocurrió el conflicto (causa raíz)\n"
            "2. Qué restricción(es) bloquea(n) la asignación\n"
            "3. Por qué el solver no pudo resolverlo\n\n"
            "Dame la respuesta en formato claro y conciso."
        )

    def _construir_prompt_relajacion(
        self,
        conflicto: str,
        restricciones: list[dict],
    ) -> str:
        return (
            "Un solver de horarios escolares no encontro solucion factible.\n\n"
            f"CONFLICTO: {conflicto}\n\n"
            f"RESTRICCIONES: {json.dumps(restricciones, ensure_ascii=False)}\n\n"
            "Devuelve UN SOLO array JSON con exactamente 2-3 sugerencias de relajacion:\n"
            "[\n"
            '  {"restriccion": "nombre", "razon": "por que", '
            '"accion_sugerida": "que hacer", "impacto_estimado": "bajo/medio/alto"},\n'
            '  ...\n'
            "]\n"
            "Responde SOLO con el JSON, sin markdown ni texto extra."
        )