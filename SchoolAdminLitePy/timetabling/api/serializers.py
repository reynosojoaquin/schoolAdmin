from rest_framework import serializers

from timetabling.models import (
    AsignacionHorario,
    Aula,
    BloqueHorario,
    Grupo,
    Materia,
    Profesor,
    RestriccionPersonalizada,
)


class ProfesorSerializer(serializers.ModelSerializer):
    materias_habilitadas = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
    )

    class Meta:
        model = Profesor
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class GrupoSerializer(serializers.ModelSerializer):
    materias = serializers.ListField(
        child=serializers.DictField(),
        required=False,
    )

    class Meta:
        model = Grupo
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class AulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aula
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class BloqueHorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloqueHorario
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class AsignacionHorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsignacionHorario
        fields = "__all__"
        read_only_fields = ("creada_en", "actualizada_en")


class RestriccionPersonalizadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestriccionPersonalizada
        fields = "__all__"
        read_only_fields = ("creada_en", "procesada")


class GenerarHorarioSerializer(serializers.Serializer):
    bloques = serializers.JSONField()
    profesores = serializers.JSONField()
    materias = serializers.JSONField()
    grupos = serializers.JSONField()
    aulas = serializers.JSONField()
    restricciones_personalizadas = serializers.JSONField(
        required=False, default=[]
    )
    tiempo_maximo_segundos = serializers.FloatField(
        required=False, default=55.0, min_value=10.0, max_value=120.0
    )

    def validate(self, attrs):
        list_fields = (
            "bloques",
            "profesores",
            "materias",
            "grupos",
            "aulas",
            "restricciones_personalizadas",
        )
        errors = {
            field: "Debe ser una lista JSON."
            for field in list_fields
            if not isinstance(attrs.get(field), list)
        }
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class EstadoJobSerializer(serializers.Serializer):
    job_id = serializers.UUIDField()
    estado = serializers.ChoiceField(
        choices=[
            ("pendiente", "Pendiente"),
            ("resolviendo", "Resolviendo"),
            ("completado", "Completado"),
            ("infactible", "Infactible"),
        ]
    )
    progreso = serializers.FloatField(default=0.0)
    mensaje = serializers.CharField(allow_blank=True, default="")


class ResultadoSerializer(serializers.Serializer):
    job_id = serializers.UUIDField()
    estado = serializers.ChoiceField(
        choices=[
            ("pendiente", "Pendiente"),
            ("resolviendo", "Resolviendo"),
            ("completado", "Completado"),
            ("infactible", "Infactible"),
        ]
    )
    asignaciones = serializers.JSONField(default=[])
    estadisticas = serializers.JSONField(default={})
    restricciones_relajadas = serializers.JSONField(default=[])


class ExplicarConflictoSerializer(serializers.Serializer):
    texto_libre = serializers.CharField(min_length=10, max_length=2000)
    asignaciones = serializers.JSONField(required=False, default=[])


class RelajacionSerializer(serializers.Serializer):
    restriccion = serializers.CharField()
    razon = serializers.CharField()
    accion_sugerida = serializers.CharField()
    impacto_estimado = serializers.CharField()
