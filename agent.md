# SchoolAdmin - contexto del proyecto

## Descripcion general

SchoolAdmin es un sistema de gestion para un centro educativo, desarrollado en Python con Django dentro del directorio `SchoolAdminLitePy`. El proyecto toma como referencia una version previa en `.NET` (`SchoolControlApp`), pero la implementacion activa y desplegable es la version Django.

La aplicacion esta pensada para operar en Docker con PostgreSQL, aunque tambien conserva compatibilidad de desarrollo local con SQLite cuando sea necesario. La web se sirve normalmente en:

```text
http://localhost:8025
```

## Estructura principal

```text
SchoolAdminLitePy/
  manage.py
  docker-compose.yml
  Dockerfile
  requirements.txt
  apps/core/
    models.py
    forms.py
    views.py
    urls.py
    admin.py
    importers.py
    migrations/
  templates/
  static/
  schooladminlite/
```

La app principal es `apps.core`. Ahi viven los modelos, formularios, vistas, rutas, importadores y configuracion del administrador de Django.

## Estado actual

El repositorio quedo actualizado y subido a GitHub en la rama `main`.

Ultimo commit subido:

```text
9954ce3 - Agregar modulos academicos y administrativos
```

Repositorio remoto:

```text
https://github.com/reynosojoaquin/schoolAdmin.git
```

Al momento de crear este archivo, el estado local de Git estaba limpio, sin cambios pendientes.

## Modulo academico

El modelo academico fue reorganizado con esta relacion:

- `Course` representa el curso o grado como nivel superior.
- `Section` depende de `Course`.
- `Subject` depende de `Section`.
- `Enrollment` ata estudiantes a secciones.
- Los docentes solo ven las secciones donde estan asignados como docentes.

Se implementaron tambien:

- Cursos y secciones ajustados a la carga horaria 2025-2026.
- Eliminacion de secciones llamadas `General`.
- Eliminacion de cursos erroneos nombrados como secciones (`1A`, `1B`, `1C`, `1D`).
- Inscripcion de estudiantes desde una seccion.
- Importacion de estudiantes marcados como nuevo ingreso.
- Campos `promoted` y `new_admission` en estudiantes.
- Registro de asistencia por seccion, pensado para docentes y dispositivos moviles.
- Calificaciones por asignatura y competencias.
- Plantillas e importacion de calificaciones.

## Fotos de personas

Estudiantes, docentes y personal administrativo manejan foto mediante el campo `photo_url`, actualmente como archivo cargado al sistema.

La interfaz permite:

- Subir foto.
- Ver foto en listados.
- Ver avatar con iniciales cuando no hay foto.
- Previsualizar la foto antes de guardar.

## Modulo administrativo

Se agrego una seccion administrativa en el menu lateral con estas opciones:

- Inventario de equipos.
- Categorias de equipos.
- Prestamos de equipos.
- Material gastable.
- Movimientos de material gastable.
- Gastos.
- Cheques.
- Cuentas bancarias.
- Conciliacion bancaria.
- Diario.
- Asignacion de personal administrativo y de apoyo.
- Orientacion y psicologia.
- Registro y generacion de reportes academicos.

### Inventario y prestamos

Modelos principales:

- `EquipmentCategory`
- `EquipmentItem`
- `EquipmentLoan`

Los prestamos actualizan el estado del equipo:

- Prestado cuando el prestamo esta activo.
- Disponible cuando se registra devolucion.

### Material gastable

Modelos principales:

- `ConsumableItem`
- `ConsumableMovement`

Los movimientos actualizan la existencia del material:

- Entrada suma existencia.
- Salida resta existencia.
- Ajuste aplica una correccion positiva o negativa.

### Contabilidad basica

Modelos principales:

- `Expense`
- `Cheque`
- `BankAccount`
- `BankReconciliation`
- `JournalEntry`

La conciliacion bancaria registra:

- Saldo banco.
- Saldo libro.
- Depositos en transito.
- Cheques pendientes.
- Cargos bancarios.
- Ajustes.
- Diferencia calculada.

El diario registra asientos simples con:

- Fecha.
- Referencia.
- Descripcion.
- Cuenta debito.
- Cuenta credito.
- Monto.
- Gasto relacionado opcional.
- Cheque relacionado opcional.

## Personal administrativo y de apoyo

El sistema ya contaba con `AdministrativeEmployee`; se amplio el flujo administrativo con `StaffAssignment` para asignar empleados a areas, funciones y periodos.

## Orientacion y psicologia

Se agrego un modulo para el departamento de orientacion y psicologia.

Modelos principales:

- `GuidanceCase`
- `GuidanceFollowUp`

El modulo permite registrar:

- Incidencias.
- Casos de apoyo.
- Referimientos.
- Situaciones familiares.
- Prioridad del caso.
- Estado del caso.
- Estudiante relacionado.
- Docente que refiere.
- Orientador o psicologo responsable.
- Descripcion del caso.
- Acciones iniciales.
- Indicador de confidencialidad.
- Fecha y notas de cierre.

Los seguimientos permiten registrar:

- Entrevistas.
- Llamadas.
- Reuniones.
- Visitas domiciliarias.
- Referimientos.
- Observaciones.
- Participantes.
- Notas.
- Proximos pasos.
- Proxima fecha de seguimiento.

El menu lateral incluye la seccion `ORIENTACION` con accesos a `Casos` y `Seguimientos`.

## Registro y reportes academicos

Se amplio el modulo de registro con generacion de reportes PDF desde el sistema.

La ruta principal es:

```text
/registro/reportes/
```

Reportes disponibles:

- Boletin de calificaciones por periodo.
- Reporte de calificaciones finales individual (RCF).
- Acta final colectiva.

Capacidades:

- Generacion colectiva por seccion.
- Generacion individual por estudiante cuando aplica.
- Salida PDF basada en los modelos suministrados por el usuario:
  - `REPORTE PERIODO 1A.pdf`
  - `Acta final de 1ro de secundaria Ord. 04-2023.pdf`
  - `29 Moya Tavarez Arianny RCF.pdf`

Archivos principales:

- `apps/core/report_pdfs.py`
- `templates/core/registry_report_form.html`
- `RegistryReportForm`
- `RegistryReportView`

La generacion usa `reportlab`, agregado a `requirements.txt`.

## Permisos y acceso

El proyecto tiene roles y permisos dinamicos. Actualmente se usan permisos existentes para controlar visibilidad:

- Gestion de personas.
- Gestion academica.
- Vista academica completa.
- Vista de secciones propias para docentes.
- Edicion/importacion/estadisticas de calificaciones.
- Gestion de usuarios y roles.

El modulo administrativo se muestra a usuarios con permisos de gestion de personas o gestion del sistema.

## Docker

Flujo habitual:

```powershell
cd SchoolAdminLitePy
docker compose up -d --build
```

El contenedor `web` ejecuta automaticamente:

- Espera de base de datos.
- Migraciones.
- Recoleccion de estaticos.
- Gunicorn.

Servicios esperados:

- `schooladminlitepy-db-1`
- `schooladminlitepy-web-1`

La aplicacion queda disponible en:

```text
http://localhost:8025
```

## Migraciones recientes importantes

Migraciones agregadas recientemente:

- `0019_section_scoped_subjects.py`
- `0020_carga_horaria_2025_2026.py`
- `0021_remove_general_sections.py`
- `0022_student_enrollment_flags.py`
- `0023_remove_section_named_courses.py`
- `0024_attendance.py`
- `0025_person_photo_file.py`
- `0026_cheque_consumableitem_equipmentcategory_expense_and_more.py`
- `0027_bankaccount_journalentry_bankreconciliation.py`
- `0028_guidancecase_guidancefollowup.py`

Tambien se corrigio `0017_competency_grade_matrix.py` para evitar SQL especifico de PostgreSQL incompatible con SQLite.

## Validaciones usadas

Comandos usados regularmente para verificar:

```powershell
cd SchoolAdminLitePy
$env:PYTHONPATH='.codex_pydeps'
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

En Docker:

```powershell
docker compose up -d --build
docker compose ps
docker compose logs --tail 120 web
```

## Notas para continuar

Prioridades naturales para siguientes pasos:

- Crear reportes del modulo administrativo.
- Mejorar conciliacion bancaria con detalle de partidas conciliatorias.
- Convertir el diario simple en diario de multiples lineas por asiento si se requiere contabilidad formal.
- Agregar permisos especificos para administracion, inventario y contabilidad.
- Agregar permisos especificos para orientacion y psicologia.
- Agregar eliminacion controlada o anulacion para registros sensibles como cheques, gastos y prestamos.
- Mejorar dashboard con indicadores administrativos.
- Crear exportaciones a Excel/PDF para inventario, gastos, cheques, asistencia, conciliaciones y casos de orientacion.
- Pulir visualmente los reportes de registro hasta igualar completamente los modelos oficiales en margenes, logos, sellos y firmas.
