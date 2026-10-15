import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.db.models import Q

from timetabling.models import AssistantMemory


SYSTEM_PROMPT = """Eres el asistente local de planificación de SchoolAdmin.
Trabajas únicamente con los datos y memorias suministrados. No inventes docentes,
secciones, asignaturas ni aulas. Propón reglas de horario de forma clara y señala
todo dato faltante. Una propuesta nunca se considera confirmada automáticamente.
Responde en español y explica qué reglas entendiste antes de sugerir generar."""


def active_memories(school_year):
    return AssistantMemory.objects.filter(
        Q(school_year="") | Q(school_year=school_year),
        active=True,
        status=AssistantMemory.CONFIRMED,
    ).order_by("-priority", "title")


def memory_context(school_year):
    memories = list(active_memories(school_year))
    if not memories:
        return "No hay reglas persistentes confirmadas."
    return "\n".join(
        f"- [{memory.get_scope_type_display()}] {memory.title}: {memory.content}"
        for memory in memories
    )


def request_local_assistant(prompt, school_year):
    endpoint = getattr(settings, "LOCAL_AI_URL", "").strip()
    model = getattr(settings, "LOCAL_AI_MODEL", "").strip()
    if not endpoint or not model:
        return {
            "available": False,
            "content": (
                "La instrucción quedó guardada. El modelo local todavía no está "
                "configurado; puedes conservarla como memoria y procesarla cuando "
                "se conecte el asistente."
            ),
        }

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": f"{SYSTEM_PROMPT}\n\nMemoria confirmada:\n{memory_context(school_year)}",
            },
            {"role": "user", "content": prompt},
        ],
    }
    request = Request(
        f"{endpoint.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result.get("message", {}).get("content", "").strip()
        if not content:
            raise ValueError("El modelo local respondió sin contenido.")
        return {"available": True, "content": content, "model": model}
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        return {
            "available": False,
            "content": f"La instrucción quedó guardada, pero el modelo local no respondió: {exc}",
        }
