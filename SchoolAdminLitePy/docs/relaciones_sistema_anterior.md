# Relaciones del sistema anterior .NET

Este documento resume las relaciones realmente declaradas en `SchoolControlDbContext.cs`.

## Relaciones declaradas por Entity Framework

### Ubicacion

- `Provincia` 1 -> N `Ciudade`
  - FK: `Ciudade.ProvinciaId`
  - Delete: `SetNull`

- `Ciudade` 1 -> N `Sectore`
  - FK: `Sectore.CiudadId`
  - Delete: `SetNull`

- `Provincia` 1 -> N `Direccione`
  - FK: `Direccione.ProvinciaId`
  - Delete: `SetNull`

- `Ciudade` 1 -> N `Direccione`
  - FK: `Direccione.CiudadId`
  - Delete: `SetNull`

- `Sectore` 1 -> N `Direccione`
  - FK: `Direccione.SectorId`
  - Delete: `SetNull`

- `TipoDireccione` 1 -> N `Direccione`
  - FK: `Direccione.TipoId`
  - Delete: `SetNull`

### Personas

- `Nacionalidade` 1 -> N `Estudiante`
  - FK: `Estudiante.NacionalidadId`
  - Delete: `SetNull`

- `LugarNacimiento` 1 -> N `Estudiante`
  - FK: `Estudiante.LugarNacimientoId`
  - Delete: `SetNull`

- `Nacionalidade` 1 -> N `Docente`
  - FK: `Docente.NacionalidadId`
  - Delete: `SetNull`

- `LugarNacimiento` 1 -> N `Docente`
  - FK: `Docente.LugarNacimientoId`
  - Delete: `SetNull`

### Contacto y telefono

- `TipoContacto` 1 -> N `Contacto`
  - FK: `Contacto.TipoId`
  - Delete: `SetNull`

- `TipoTelefono` 1 -> N `Telefono`
  - FK: `Telefono.TipoId`
  - Delete: `SetNull`

Nota: `Contacto.PersonaId`, `Telefono.PersonaId` y `Direccione.PersonaId` existen como columnas, pero en `SchoolControlDbContext.cs` no tienen relacion EF configurada hacia `Persona`, `Estudiante` o `Docente`.

### Curriculum

- `Curriculum` 1 -> N `CurriculumDetalle`
  - FK: `CurriculumDetalle.CurriculumId`
  - Delete: `SetNull`

- `CurriculumInstitucione` 1 -> N `CurriculumDetalle`
  - FK: `CurriculumDetalle.InstitucionId`

- `Curriculumtipo` 1 -> N `CurriculumDetalle`
  - FK: `CurriculumDetalle.TipoCurriculumId`
  - Delete: `SetNull`

Nota: `Curriculum.EmpleadoId` existe como columna, pero en `SchoolControlDbContext.cs` no tiene relacion EF configurada hacia empleados/docentes/personas.

### Usuarios

- `Role` 1 -> N `User`
  - FK: `User.RoleId`
  - Delete: `SetNull`

- `User` 1 -> N `UsersCredential`
  - FK: `UsersCredential.UserId`
  - Delete: `SetNull`

- `User` 1 -> N `PendingEmailConfirmation`
  - FK: `PendingEmailConfirmation.UserId`
  - Delete: `SetNull`

## Campos que parecen FK, pero no tienen relacion declarada

Estos campos existen en las clases o tablas, pero no aparecen con `HasOne(...).HasForeignKey(...)` en el contexto:

- `Asignaturas.Cursoid`
- `Asignaturas.Responsable`
- `Curso.Responsable`
- `Asignaturacompetencia.Asignaturaid`
- `Asignaturacompetencia.Competenciaid`
- `Calificaciones.Estudianteid`
- `Calificaciones.Asigcompid`
- `Contacto.PersonaId`
- `Telefono.PersonaId`
- `Direccione.PersonaId`
- `Empleado.PersonaId`
- `Empleado.TipoEmpleadoId`
- `Empleado.PosicionId`
- `PosicionesEmpledo.TipoEmpleadoId`
- `Curriculum.EmpleadoId`

## Implicaciones para SchoolAdminLitePy

### Replicado directamente

- Provincias, ciudades, sectores y direcciones.
- Nacionalidades y lugares de nacimiento para estudiantes/docentes.
- Tipos de direccion, telefono y contacto.
- Curriculum, detalles, instituciones y tipos.

### Mejoras conscientes sobre el modelo anterior

- Django usa su autenticacion nativa en lugar de copiar `User`, `Role` y `UsersCredential`.
- `Student`, `Teacher` y `AdministrativeEmployee` reutilizan una base comun de campos personales.
- Direcciones, telefonos y contactos se relacionan directamente con estudiantes/docentes/empleados, porque el modelo anterior tenia `PersonaId` sin FK declarada.
- `Section` y `TeachingAssignment` son nuevas estructuras del nuevo sistema. No existian formalmente en el modelo .NET.

### Nueva relacion academica propuesta

Para soportar secciones y docencia sin depender de campos sueltos:

- `Course` 1 -> N `Section`
- `Course` 1 -> N `Subject`
- `Section` + `Subject` -> `Teacher` mediante `TeachingAssignment`

Regla de integridad:

- Una asignatura solo puede asignarse a una seccion si ambas pertenecen al mismo curso.

