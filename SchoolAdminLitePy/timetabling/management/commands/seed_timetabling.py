"""Seed timetabling models from core data."""
import random
from django.core.management.base import BaseCommand
from apps.core.models import Teacher, Course, Section, Subject, TeachingAssignment
from timetabling.models import (
    Profesor, Materia, Grupo, Aula, BloqueHorario,
    AsignacionMateriaGrupo,
)


class Command(BaseCommand):
    help = "Seed timetabling data from core models"

    def handle(self, *args, **options):
        self._seed_materias()
        self._seed_grupos()
        self._seed_asignaciones_materia_grupo()
        self._seed_profesores()
        self._seed_bloques()
        self._seed_aulas()
        self._print_summary()

    def _seed_materias(self):
        if Materia.objects.exists():
            self.stdout.write("Materias already exist, skipping")
            return
        subjects = Subject.objects.all()
        materia_map = {}
        for s in subjects:
            base = s.name.split(" - ")[0].strip() if " - " in s.name else s.name
            if base not in materia_map:
                materia_map[base] = Materia.objects.create(
                    nombre=base,
                    horas_semanales_requeridas=s.weekly_hours or 4,
                    franja_preferente="mañana",
                    activa=True,
                )
        self.stdout.write(self.style.SUCCESS(f"Materias: {len(materia_map)} created"))

    def _seed_grupos(self):
        if Grupo.objects.exists():
            self.stdout.write("Grupos already exist, skipping")
            return
        course_names = {}
        for c in Course.objects.all():
            course_names[c.pk] = c.name if hasattr(c, 'name') and c.name else str(c.pk)
        for sec in Section.objects.select_related("course").all():
            grade = course_names.get(sec.course_id, str(sec.course_id))
            Grupo.objects.create(
                nombre=sec.name,
                grado=grade,
                activo=True,
            )
        self.stdout.write(self.style.SUCCESS(f"Grupos: {Grupo.objects.count()} created"))

    def _seed_asignaciones_materia_grupo(self):
        count = 0
        seen = set()
        for s in Subject.objects.select_related("section").all():
            base = s.name.split(" - ")[0].strip() if " - " in s.name else s.name
            materia = Materia.objects.filter(nombre=base).first()
            grupo = Grupo.objects.filter(nombre=s.section.name).first()
            if materia and grupo:
                key = (materia.pk, grupo.pk)
                if key not in seen:
                    AsignacionMateriaGrupo.objects.update_or_create(
                        materia=materia,
                        grupo=grupo,
                        defaults={"horas_asignadas": s.weekly_hours or 4},
                    )
                    count += 1
                    seen.add(key)
        self.stdout.write(self.style.SUCCESS(f"Asignaciones materia-grupo: {count} created"))

    def _seed_profesores(self):
        if Profesor.objects.exists():
            self.stdout.write("Profesores already exist, skipping")
            return
        all_materias = list(Materia.objects.all())
        dias = ["LUN", "MAR", "MIÉ", "JUE", "VIE"]
        for t in Teacher.objects.all():
            disponibilidad = {}
            for dia in dias:
                disponibilidad[dia] = [j for j in range(1, 9)]
            prof = Profesor.objects.create(
                nombre=f"{t.first_name} {t.last_name}".strip() or f"Prof {t.pk}",
                disponibilidad=disponibilidad,
                horas_max_dia=6,
                horas_max_semana=30,
                activo=True,
            )
            assigned = set()
            for ta in t.teaching_assignments.all():
                base = ta.subject.name.split(" - ")[0].strip() if " - " in ta.subject.name else ta.subject.name
                m = Materia.objects.filter(nombre=base).first()
                if m and m.pk not in assigned:
                    prof.materias_habilitadas.add(m)
                    assigned.add(m.pk)
            if not assigned and all_materias:
                chosen = random.sample(all_materias, min(3, len(all_materias)))
                prof.materias_habilitadas.set(chosen)
        self.stdout.write(self.style.SUCCESS(f"Profesores: {Profesor.objects.count()} created"))

    def _seed_bloques(self):
        if BloqueHorario.objects.exists():
            self.stdout.write("Bloques already exist, skipping")
            return
        dias = ["LUN", "MAR", "MIÉ", "JUE", "VIE"]
        for dia in dias:
            for hora in range(7, 15):
                BloqueHorario.objects.create(
                    dia=dia,
                    hora_inicio=f"{hora:02d}:00",
                    hora_fin=f"{hora+1:02d}:00",
                    orden=hora - 6,
                    activo=True,
                )
        self.stdout.write(self.style.SUCCESS(f"Bloques: {BloqueHorario.objects.count()} created"))

    def _seed_aulas(self):
        if Aula.objects.exists():
            self.stdout.write("Aulas already exist, skipping")
            return
        aulas_data = [
            ("Aula 101", "normal", 40),
            ("Aula 102", "normal", 40),
            ("Aula 103", "normal", 35),
            ("Aula 201", "normal", 40),
            ("Aula 202", "normal", 40),
            ("Lab Ciencias", "laboratorio", 30),
            ("Lab Computación", "laboratorio", 30),
            ("Auditorio", "auditorio", 100),
        ]
        for nombre, tipo, cap in aulas_data:
            Aula.objects.create(nombre=nombre, tipo=tipo, capacidad=cap, activa=True)
        self.stdout.write(self.style.SUCCESS(f"Aulas: {Aula.objects.count()} created"))

    def _print_summary(self):
        self.stdout.write("\n" + "=" * 40)
        self.stdout.write("RESUMEN:")
        self.stdout.write(f"  Profesores: {Profesor.objects.count()}")
        self.stdout.write(f"  Materias: {Materia.objects.count()}")
        self.stdout.write(f"  Grupos: {Grupo.objects.count()}")
        self.stdout.write(f"  Aulas: {Aula.objects.count()}")
        self.stdout.write(f"  Bloques: {BloqueHorario.objects.count()}")
        self.stdout.write(f"  Asignaciones materia-grupo: {AsignacionMateriaGrupo.objects.count()}")
