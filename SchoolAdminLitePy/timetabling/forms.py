from django import forms
from django.core.exceptions import ValidationError

from timetabling.constants import DIAS_SEMANA
from timetabling.models import Aula, BloqueHorario, Grupo, Profesor


class AvailabilityFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        availability = getattr(self.instance, "disponibilidad", {}) or {}
        self.available_orders_by_day = {}

        for day, label in DIAS_SEMANA:
            blocks = BloqueHorario.objects.filter(dia=day).order_by("orden")
            available_orders = [str(block.orden) for block in blocks]
            self.available_orders_by_day[day] = available_orders
            choices = [
                (
                    order,
                    f"Bloque {block.orden} ({block.hora_inicio:%H:%M}-{block.hora_fin:%H:%M})",
                )
                for block, order in zip(blocks, available_orders)
            ]
            restriction_name = f"limitar_{day}"
            blocks_name = f"bloques_{day}"
            day_is_restricted = (
                bool(availability)
                and (
                    day not in availability
                    or {
                        str(order) for order in availability.get(day, [])
                    } != set(available_orders)
                )
            )
            self.fields[restriction_name] = forms.BooleanField(
                label=f"Restringir {label}",
                required=False,
                initial=day_is_restricted,
                widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
            )
            self.fields[blocks_name] = forms.MultipleChoiceField(
                label=f"Bloques disponibles — {label}",
                required=False,
                choices=choices,
                initial=(
                    [str(order) for order in availability[day]]
                    if day in availability
                    else ([] if availability else available_orders)
                ),
                widget=forms.CheckboxSelectMultiple,
                help_text="Desmarca «Restringir» para permitir todos los bloques. Si restringes el día y no marcas ninguno, no estará disponible ese día.",
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        restricted_days = {
            day
            for day, _ in DIAS_SEMANA
            if self.cleaned_data[f"limitar_{day}"]
        }
        instance.disponibilidad = (
            {
                day: [
                    int(order)
                    for order in (
                        self.cleaned_data[f"bloques_{day}"]
                        if day in restricted_days
                        else self.available_orders_by_day[day]
                    )
                ]
                for day, _ in DIAS_SEMANA
            }
            if restricted_days
            else {}
        )
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class AulaForm(AvailabilityFormMixin, forms.ModelForm):
    capacidad = forms.IntegerField(min_value=1, label="Capacidad")

    class Meta:
        model = Aula
        fields = ["nombre", "tipo", "capacidad", "activa"]
        widgets = {
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        duplicates = Aula.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError("Ya existe un aula con ese nombre.")
        return nombre


class BloqueHorarioForm(forms.ModelForm):
    class Meta:
        model = BloqueHorario
        fields = ["dia", "orden", "hora_inicio", "hora_fin", "activo"]
        widgets = {
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fin": forms.TimeInput(attrs={"type": "time"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("hora_inicio")
        end = cleaned_data.get("hora_fin")
        day = cleaned_data.get("dia")
        active = cleaned_data.get("activo")

        if start and end and start >= end:
            self.add_error("hora_fin", "La hora final debe ser posterior a la hora de inicio.")

        if start and end and day and active:
            overlapping_blocks = BloqueHorario.objects.filter(dia=day, activo=True)
            if self.instance.pk:
                overlapping_blocks = overlapping_blocks.exclude(pk=self.instance.pk)
            for block in overlapping_blocks:
                if start < block.hora_fin and end > block.hora_inicio:
                    self.add_error(
                        "hora_inicio",
                        f"El horario se superpone con el bloque {block.orden} "
                        f"({block.hora_inicio:%H:%M}-{block.hora_fin:%H:%M}).",
                    )
                    break
        return cleaned_data


class ProfesorHorarioForm(AvailabilityFormMixin, forms.ModelForm):
    horas_max_dia = forms.IntegerField(min_value=1, label="Máximo de horas por día")
    horas_max_semana = forms.IntegerField(min_value=1, label="Máximo de horas por semana")

    class Meta:
        model = Profesor
        fields = ["horas_max_dia", "horas_max_semana"]


class GrupoHorarioForm(AvailabilityFormMixin, forms.ModelForm):
    class Meta:
        model = Grupo
        fields = []
