from django.core.exceptions import ValidationError
from django.db import models

from timetabling.constants import DIAS_SEMANA, TIPOS_AULA


class Profesor(models.Model):
    nombre = models.CharField("nombre", max_length=200)
    materias_habilitadas = models.ManyToManyField(
        "Materia",
        related_name="profesores_habilitados",
        verbose_name="materias habilitadas",
        blank=True,
    )
    disponibilidad = models.JSONField(
        "disponibilidad",
        default=dict,
        blank=True,
        help_text='{"LUN": [0, 1, 2], "MAR": [3, 4]}'
        ' — lista de indices de bloques disponibles por dia',
    )
    horas_max_dia = models.PositiveSmallIntegerField(
        "horas maximas por dia",
        default=6,
    )
    horas_max_semana = models.PositiveSmallIntegerField(
        "horas maximas por semana",
        default=24,
    )
    activo = models.BooleanField("activo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "profesor"
        verbose_name_plural = "profesores"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Materia(models.Model):
    nombre = models.CharField("nombre", max_length=200)
    horas_semanales_requeridas = models.PositiveSmallIntegerField(
        "horas semanales requeridas",
    )
    franja_preferente = models.CharField(
        "franja horaria preferente",
        max_length=20,
        blank=True,
        help_text="mañana, tarde, mixto",
    )
    activa = models.BooleanField("activa", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "materia"
        verbose_name_plural = "materias"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Grupo(models.Model):
    nombre = models.CharField("nombre", max_length=50)
    grado = models.CharField("grado", max_length=20)
    materias = models.ManyToManyField(
        "Materia",
        through="AsignacionMateriaGrupo",
        verbose_name="materias",
    )
    activo = models.BooleanField("activo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "grupo"
        verbose_name_plural = "grupos"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class AsignacionMateriaGrupo(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="+")
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="asignaciones_materia")
    horas_asignadas = models.PositiveSmallIntegerField("horas asignadas")

    class Meta:
        verbose_name = "asignacion materia-grupo"
        verbose_name_plural = "asignaciones materia-grupo"
        unique_together = [("materia", "grupo")]

    def __str__(self) -> str:
        return f"{self.grupo.nombre} - {self.materia.nombre} ({self.horas_asignadas}h)"


class Aula(models.Model):
    nombre = models.CharField("nombre", max_length=100)
    tipo = models.CharField(
        "tipo",
        max_length=20,
        choices=TIPOS_AULA,
        default=TIPOS_AULA[0][0],
    )
    capacidad = models.PositiveIntegerField("capacidad")
    activa = models.BooleanField("activa", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "aula"
        verbose_name_plural = "aulas"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class BloqueHorario(models.Model):
    dia = models.CharField("dia", max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField("hora inicio")
    hora_fin = models.TimeField("hora fin")
    orden = models.PositiveSmallIntegerField("orden dentro del dia")
    activo = models.BooleanField("activo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "bloque horario"
        verbose_name_plural = "bloques horario"
        ordering = ["dia", "orden"]
        unique_together = [("dia", "orden")]

    def __str__(self) -> str:
        return f"{self.dia} {self.hora_inicio}-{self.hora_fin}"


class AsignacionHorario(models.Model):
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name="asignaciones")
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="asignaciones")
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="asignaciones")
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name="asignaciones")
    bloque = models.ForeignKey(BloqueHorario, on_delete=models.CASCADE, related_name="asignaciones")
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "asignacion horario"
        verbose_name_plural = "asignaciones horario"
        ordering = ["bloque__dia", "bloque__orden"]
        indexes = [
            models.Index(fields=["profesor", "bloque"]),
            models.Index(fields=["grupo", "bloque"]),
            models.Index(fields=["aula", "bloque"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["profesor", "bloque"],
                name="unique_profesor_bloque",
            ),
            models.UniqueConstraint(
                fields=["grupo", "bloque"],
                name="unique_grupo_bloque",
            ),
            models.UniqueConstraint(
                fields=["aula", "bloque"],
                name="unique_aula_bloque",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.profesor.nombre} / {self.materia.nombre} / {self.grupo.nombre} / {self.bloque}"

    def clean(self) -> None:
        if self.profesor_id == self.grupo_id:
            pass
        if self.profesor.disponibilidad:
            bloque = self.bloque
            dia_bloques = self.profesor.disponibilidad.get(self.bloque.dia, [])
            # Validacion basica de disponibilidad
            if dia_bloques and self.bloque.orden not in dia_bloques:
                raise ValidationError(
                    f"El profesor {self.profesor.nombre} no tiene disponibilidad "
                    f"en {self.bloque.dia} bloque {self.bloque.orden}"
                )


class RestriccionPersonalizada(models.Model):
    texto_libre = models.TextField("texto libre")
    regla_json = models.JSONField("regla JSON", default=dict, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    procesada = models.BooleanField("procesada", default=False)

    class Meta:
        verbose_name = "restriccion personalizada"
        verbose_name_plural = "restricciones personalizadas"
        ordering = ["-creada_en"]

    def __str__(self) -> str:
        return self.texto_libre[:80]


class HorarioJob(models.Model):
    job_id = models.UUIDField(primary_key=True)
    estado = models.CharField(max_length=20, default="pendiente")
    progreso = models.FloatField(default=0.0)
    mensaje = models.CharField(max_length=300, blank=True, default="")
    datos = models.JSONField(default=dict, blank=True)
    asignaciones = models.JSONField(default=list, blank=True)
    estadisticas = models.JSONField(default=dict, blank=True)
    restricciones_relajadas = models.JSONField(default=list, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "horario job"
        verbose_name_plural = "horarios jobs"
        ordering = ["-creado_en"]

    def __str__(self) -> str:
        return f"Job {self.job_id} - {self.estado}"