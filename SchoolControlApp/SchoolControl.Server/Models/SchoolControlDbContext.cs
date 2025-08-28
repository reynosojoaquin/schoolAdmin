using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;

namespace SchoolControl.Server.Models;

public partial class SchoolControlDbContext : DbContext
{
    public SchoolControlDbContext()
    {
    }

    public SchoolControlDbContext(DbContextOptions<SchoolControlDbContext> options)
        : base(options)
    {
    }

    public virtual DbSet<Accione> Acciones { get; set; }

    public virtual DbSet<Asignatura> Asignaturas { get; set; }

    public virtual DbSet<AsignaturasCompetencia> AsignaturasCompetencias { get; set; }

    public virtual DbSet<Calificacione> Calificaciones { get; set; }

    public virtual DbSet<Ciudade> Ciudades { get; set; }

    public virtual DbSet<Competencia> Competencias { get; set; }

    public virtual DbSet<Contacto> Contactos { get; set; }

    public virtual DbSet<Curriculum> Curricula { get; set; }

    public virtual DbSet<CurriculumDetalle> CurriculumDetalles { get; set; }

    public virtual DbSet<CurriculumInstitucione> CurriculumInstituciones { get; set; }

    public virtual DbSet<Curriculumtipo> Curriculumtipos { get; set; }

    public virtual DbSet<Curso> Cursos { get; set; }

    public virtual DbSet<Direccione> Direcciones { get; set; }

    public virtual DbSet<Docente> Docentes { get; set; }

    public virtual DbSet<EmpleadosAdm> EmpleadosAdms { get; set; }

    public virtual DbSet<Estudiante> Estudiantes { get; set; }

    public virtual DbSet<HistoriaClinica> HistoriaClinicas { get; set; }

    public virtual DbSet<LugarNacimiento> LugarNacimientos { get; set; }

    public virtual DbSet<Nacionalidade> Nacionalidades { get; set; }

    public virtual DbSet<Padre> Padres { get; set; }

    public virtual DbSet<PendingEmailConfirmation> PendingEmailConfirmations { get; set; }

    public virtual DbSet<Permiso> Permisos { get; set; }

    public virtual DbSet<PermisosAccione> PermisosAcciones { get; set; }

    public virtual DbSet<PermisosUsuario> PermisosUsuarios { get; set; }

    public virtual DbSet<Permisossistema> Permisossistemas { get; set; }

    public virtual DbSet<PosicionesEmpledo> PosicionesEmpledos { get; set; }

    public virtual DbSet<Provincia> Provincias { get; set; }

    public virtual DbSet<RegistrosEncontrado> RegistrosEncontrados { get; set; }

    public virtual DbSet<Role> Roles { get; set; }

    public virtual DbSet<RolesPermiso> RolesPermisos { get; set; }

    public virtual DbSet<SeccionesCurso> SeccionesCursos { get; set; }

    public virtual DbSet<Sectore> Sectores { get; set; }

    public virtual DbSet<Telefono> Telefonos { get; set; }

    public virtual DbSet<TipoContacto> TipoContactos { get; set; }

    public virtual DbSet<TipoDireccione> TipoDirecciones { get; set; }

    public virtual DbSet<TipoTelefono> TipoTelefonos { get; set; }

    public virtual DbSet<TiposEmpledo> TiposEmpledos { get; set; }

    public virtual DbSet<User> Users { get; set; }

    public virtual DbSet<UserPermission> UserPermissions { get; set; }

    public virtual DbSet<UsersCredential> UsersCredentials { get; set; }

    public virtual DbSet<UsuarioPermiso> UsuarioPermisos { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
#warning To protect potentially sensitive information in your connection string, you should move it out of source code. You can avoid scaffolding the connection string by using the Name= syntax to read it from configuration - see https://go.microsoft.com/fwlink/?linkid=2131148. For more guidance on storing connection strings, see https://go.microsoft.com/fwlink/?LinkId=723263.
        => optionsBuilder.UseNpgsql("Host=localhost;Database=SchoolControlDB;Port=5432;Username=postgres;Password=admin");

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Accione>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("acciones_pk");

            entity.ToTable("acciones");

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.Descripcion)
                .HasColumnType("character varying")
                .HasColumnName("descripcion");
        });

        modelBuilder.Entity<Asignatura>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("asignatura_pk");

            entity.ToTable("asignatura");

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.Cursoid).HasColumnName("cursoid");
            entity.Property(e => e.Icon)
                .HasColumnType("character varying")
                .HasColumnName("icon");
            entity.Property(e => e.Nombre)
                .HasColumnType("character varying")
                .HasColumnName("nombre");
            entity.Property(e => e.Responsable).HasColumnName("responsable");
        });

        modelBuilder.Entity<AsignaturasCompetencia>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("asignaturas_competencias_pk");

            entity.ToTable("asignaturas_competencias");

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.Asignaturaid).HasColumnName("asignaturaid");
            entity.Property(e => e.Competenciaid).HasColumnName("competenciaid");
            entity.Property(e => e.Cursoid).HasColumnName("cursoid");
        });

        modelBuilder.Entity<Calificacione>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("calificaciones_pk");

            entity.ToTable("calificaciones");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.AsigCompId).HasColumnName("asig_comp_id");
            entity.Property(e => e.CursoId).HasColumnName("curso_id");
            entity.Property(e => e.Estudianteid).HasColumnName("estudianteid");
            entity.Property(e => e.Final).HasColumnName("final");
            entity.Property(e => e.P1).HasColumnName("p1");
            entity.Property(e => e.P2).HasColumnName("p2");
            entity.Property(e => e.P3).HasColumnName("p3");
            entity.Property(e => e.P4).HasColumnName("p4");
            entity.Property(e => e.Pp1).HasColumnName("pp1");
            entity.Property(e => e.Pp2).HasColumnName("pp2");
            entity.Property(e => e.Pp3).HasColumnName("pp3");
            entity.Property(e => e.Pp4).HasColumnName("pp4");
            entity.Property(e => e.Rp1).HasColumnName("rp1");
            entity.Property(e => e.Rp2).HasColumnName("rp2");
            entity.Property(e => e.Rp3).HasColumnName("rp3");
            entity.Property(e => e.Rp4).HasColumnName("rp4");
        });

        modelBuilder.Entity<Ciudade>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("ciudades_pkey");

            entity.ToTable("ciudades");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Nombre).HasColumnName("nombre");
            entity.Property(e => e.ProvinciaId).HasColumnName("provincia_id");

            entity.HasOne(d => d.Provincia).WithMany(p => p.Ciudades)
                .HasForeignKey(d => d.ProvinciaId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("ciudades_provincia_id_fkey");
        });

        modelBuilder.Entity<Competencia>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("comptencias_pk");

            entity.ToTable("competencias");

            entity.Property(e => e.Id)
                .ValueGeneratedNever()
                .HasColumnName("id");
            entity.Property(e => e.Descripcion)
                .HasColumnType("character varying")
                .HasColumnName("descripcion");
        });

        modelBuilder.Entity<Contacto>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("contactos_pkey");

            entity.ToTable("contactos");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Apellido).HasColumnName("apellido");
            entity.Property(e => e.Direccion).HasColumnName("direccion");
            entity.Property(e => e.Nombre).HasColumnName("nombre");
            entity.Property(e => e.PersonaId).HasColumnName("persona_id");
            entity.Property(e => e.Telefono).HasColumnName("telefono");
            entity.Property(e => e.TipoId).HasColumnName("tipo_id");

            entity.HasOne(d => d.Tipo).WithMany(p => p.Contactos)
                .HasForeignKey(d => d.TipoId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("contactos_tipo_id_fkey");
        });

        modelBuilder.Entity<Curriculum>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("curriculum_pkey");

            entity.ToTable("curriculum");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CarpetasCurriculum).HasColumnName("carpetas_curriculum");
            entity.Property(e => e.EmpleadoId).HasColumnName("empleado_id");
        });

        modelBuilder.Entity<CurriculumDetalle>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("curriculum_detalle_pkey");

            entity.ToTable("curriculum_detalle");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CurriculumId).HasColumnName("curriculum_id");
            entity.Property(e => e.Descripcion).HasColumnName("descripcion");
            entity.Property(e => e.Eliminado).HasColumnName("eliminado");
            entity.Property(e => e.Fecha).HasColumnName("fecha");
            entity.Property(e => e.InstitucionId).HasColumnName("institucion_id");
            entity.Property(e => e.TipoCurriculumId).HasColumnName("tipo_curriculum_id");
            entity.Property(e => e.UrlFile).HasColumnName("url_file");

            entity.HasOne(d => d.Curriculum).WithMany(p => p.CurriculumDetalles)
                .HasForeignKey(d => d.CurriculumId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("curriculum_detalle_curriculum_id_fkey");

            entity.HasOne(d => d.Institucion).WithMany(p => p.CurriculumDetalles)
                .HasForeignKey(d => d.InstitucionId)
                .HasConstraintName("curriculum_detalle_institucion_id_fkey");

            entity.HasOne(d => d.TipoCurriculum).WithMany(p => p.CurriculumDetalles)
                .HasForeignKey(d => d.TipoCurriculumId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("curriculum_detalle_tipo_curriculum_id_fkey");
        });

        modelBuilder.Entity<CurriculumInstitucione>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("curriculum_instituciones_pkey");

            entity.ToTable("curriculum_instituciones");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Descripcion).HasColumnName("descripcion");
            entity.Property(e => e.Eliminado).HasColumnName("eliminado");
        });

        modelBuilder.Entity<Curriculumtipo>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("curriculumtipo_pkey");

            entity.ToTable("curriculumtipo");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Descripcion).HasColumnName("descripcion");
        });

        modelBuilder.Entity<Curso>(entity =>
        {
            entity.HasKey(e => e.Cursoid).HasName("newtable_pk");

            entity.ToTable("cursos");

            entity.Property(e => e.Cursoid)
                .UseIdentityAlwaysColumn()
                .HasColumnName("cursoid");
            entity.Property(e => e.Nombre)
                .HasColumnType("character varying")
                .HasColumnName("nombre");
            entity.Property(e => e.Orden).HasColumnName("orden");
        });

        modelBuilder.Entity<Direccione>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("direcciones_pkey");

            entity.ToTable("direcciones");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Apartamento).HasColumnName("apartamento");
            entity.Property(e => e.Calle).HasColumnName("calle");
            entity.Property(e => e.CiudadId).HasColumnName("ciudad_id");
            entity.Property(e => e.Latitude).HasColumnName("latitude");
            entity.Property(e => e.Longitud).HasColumnName("longitud");
            entity.Property(e => e.Numero).HasColumnName("numero");
            entity.Property(e => e.PersonaId).HasColumnName("persona_id");
            entity.Property(e => e.ProvinciaId).HasColumnName("provincia_id");
            entity.Property(e => e.SectorId).HasColumnName("sector_id");
            entity.Property(e => e.TipoId).HasColumnName("tipo_id");

            entity.HasOne(d => d.Ciudad).WithMany(p => p.Direcciones)
                .HasForeignKey(d => d.CiudadId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("direcciones_ciudad_id_fkey");

            entity.HasOne(d => d.Provincia).WithMany(p => p.Direcciones)
                .HasForeignKey(d => d.ProvinciaId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("direcciones_provincia_id_fkey");

            entity.HasOne(d => d.Sector).WithMany(p => p.Direcciones)
                .HasForeignKey(d => d.SectorId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("direcciones_sector_id_fkey");

            entity.HasOne(d => d.Tipo).WithMany(p => p.Direcciones)
                .HasForeignKey(d => d.TipoId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("direcciones_tipo_id_fkey");
        });

        modelBuilder.Entity<Docente>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("personas_pkey");

            entity.HasIndex(e => e.Cedula, "personas_cedula_key").IsUnique();

            entity.Property(e => e.Id)
                .HasDefaultValueSql("nextval('personas_id_seq'::regclass)")
                .HasColumnName("id");
            entity.Property(e => e.Activo).HasColumnName("activo");
            entity.Property(e => e.Apellidos).HasColumnName("apellidos");
            entity.Property(e => e.Cedula).HasColumnName("cedula");
            entity.Property(e => e.Correo).HasColumnName("correo");
            entity.Property(e => e.Direccion)
                .HasColumnType("character varying")
                .HasColumnName("direccion");
            entity.Property(e => e.EstadoCivil).HasColumnName("estado_civil");
            entity.Property(e => e.FechaIngreso).HasColumnName("fecha_ingreso");
            entity.Property(e => e.FechaNacimiento).HasColumnName("fecha_nacimiento");
            entity.Property(e => e.Licencia).HasColumnName("licencia");
            entity.Property(e => e.LugarNacimientoId).HasColumnName("lugar_nacimiento_id");
            entity.Property(e => e.NacionalidadId).HasColumnName("nacionalidad_id");
            entity.Property(e => e.Nombres).HasColumnName("nombres");
            entity.Property(e => e.Sexo).HasColumnName("sexo");
            entity.Property(e => e.Telefono)
                .HasColumnType("character varying")
                .HasColumnName("telefono");
            entity.Property(e => e.Url).HasColumnName("url");
            entity.Property(e => e.Userid).HasColumnName("userid");

            entity.HasOne(d => d.LugarNacimiento).WithMany(p => p.Docentes)
                .HasForeignKey(d => d.LugarNacimientoId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("personas_lugar_nacimiento_id_fkey");

            entity.HasOne(d => d.Nacionalidad).WithMany(p => p.Docentes)
                .HasForeignKey(d => d.NacionalidadId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("personas_nacionalidad_id_fkey");
        });

        modelBuilder.Entity<EmpleadosAdm>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("empleados_pkey");

            entity.ToTable("empleados_adm");

            entity.HasIndex(e => e.Cedula, "empleados_cedula_key").IsUnique();

            entity.Property(e => e.Id)
                .HasDefaultValueSql("nextval('empleados_id_seq'::regclass)")
                .HasColumnName("id");
            entity.Property(e => e.Activo).HasColumnName("activo");
            entity.Property(e => e.Apellidos).HasColumnName("apellidos");
            entity.Property(e => e.Cedula).HasColumnName("cedula");
            entity.Property(e => e.Correo).HasColumnName("correo");
            entity.Property(e => e.EstadoCivil).HasColumnName("estado_civil");
            entity.Property(e => e.FechaNacimiento).HasColumnName("fecha_nacimiento");
            entity.Property(e => e.Licencia).HasColumnName("licencia");
            entity.Property(e => e.LugarNacimientoId).HasColumnName("lugar_nacimiento_id");
            entity.Property(e => e.NacionalidadId).HasColumnName("nacionalidad_id");
            entity.Property(e => e.Nombres).HasColumnName("nombres");
            entity.Property(e => e.Sexo).HasColumnName("sexo");
            entity.Property(e => e.Url).HasColumnName("url");
        });

        modelBuilder.Entity<Estudiante>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("estudiante_pkey");

            entity.ToTable("estudiantes");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Activo).HasColumnName("activo");
            entity.Property(e => e.Apellidos).HasColumnName("apellidos");
            entity.Property(e => e.Cedula).HasColumnName("cedula");
            entity.Property(e => e.Correo).HasColumnName("correo");
            entity.Property(e => e.Cursoid).HasColumnName("cursoid");
            entity.Property(e => e.Esnuevoingreso).HasColumnName("esnuevoingreso");
            entity.Property(e => e.EstadoCivil).HasColumnName("estado_civil");
            entity.Property(e => e.FechaNacimiento).HasColumnName("fecha_nacimiento");
            entity.Property(e => e.Licencia).HasColumnName("licencia");
            entity.Property(e => e.LugarNacimientoId).HasColumnName("lugar_nacimiento_id");
            entity.Property(e => e.NacionalidadId).HasColumnName("nacionalidad_id");
            entity.Property(e => e.Nombres).HasColumnName("nombres");
            entity.Property(e => e.NumOrden).HasColumnName("num_orden");
            entity.Property(e => e.Promovido).HasColumnName("promovido");
            entity.Property(e => e.Sexo).HasColumnName("sexo");
            entity.Property(e => e.SigerdId)
                .HasColumnType("character varying")
                .HasColumnName("sigerd_id");
            entity.Property(e => e.Url).HasColumnName("url");

            entity.HasOne(d => d.LugarNacimiento).WithMany(p => p.Estudiantes)
                .HasForeignKey(d => d.LugarNacimientoId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("estudainte_lugar_nacimiento_id_fkey");

            entity.HasOne(d => d.Nacionalidad).WithMany(p => p.Estudiantes)
                .HasForeignKey(d => d.NacionalidadId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("estudiante_nacionalidad_id_fkey");
        });

        modelBuilder.Entity<HistoriaClinica>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("historia_clinica_pk");

            entity.ToTable("historia_clinica");

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.Descripcion)
                .HasColumnType("character varying")
                .HasColumnName("descripcion");
            entity.Property(e => e.EstudianteId).HasColumnName("estudiante_id");
            entity.Property(e => e.Tipo)
                .HasColumnType("character varying")
                .HasColumnName("tipo");

            entity.HasOne(d => d.Estudiante).WithMany(p => p.HistoriaClinicas)
                .HasForeignKey(d => d.EstudianteId)
                .HasConstraintName("historia_clinica_estudiantes_fk");
        });

        modelBuilder.Entity<LugarNacimiento>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("lugar_nacimiento_pkey");

            entity.ToTable("lugar_nacimiento");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.LugarNacimientoId).HasColumnName("lugar_nacimiento_id");
            entity.Property(e => e.Nombre).HasColumnName("nombre");
        });

        modelBuilder.Entity<Nacionalidade>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("nacionalidades_pkey");

            entity.ToTable("nacionalidades");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Cod).HasColumnName("COD");
            entity.Property(e => e.Nombre).HasColumnName("nombre");
        });

        modelBuilder.Entity<Padre>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("padres_pk");

            entity.ToTable("padres");

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.Apellido)
                .HasColumnType("character varying")
                .HasColumnName("apellido");
            entity.Property(e => e.EstudianteId).HasColumnName("estudiante_id");
            entity.Property(e => e.Nombre)
                .HasColumnType("character varying")
                .HasColumnName("nombre");
            entity.Property(e => e.Parentesco)
                .HasColumnType("character varying")
                .HasColumnName("parentesco");
            entity.Property(e => e.Telefono)
                .HasColumnType("character varying")
                .HasColumnName("telefono");

            entity.HasOne(d => d.Estudiante).WithMany(p => p.Padres)
                .HasForeignKey(d => d.EstudianteId)
                .HasConstraintName("padres_estudiantes_fk");
        });

        modelBuilder.Entity<PendingEmailConfirmation>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("pending_email_confirmations_pkey");

            entity.ToTable("pending_email_confirmations");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.Property(e => e.UniqueCode).HasColumnName("unique_code");
            entity.Property(e => e.UpdatedAt).HasColumnName("updated_at");
            entity.Property(e => e.UserId).HasColumnName("user_id");

            entity.HasOne(d => d.User).WithMany(p => p.PendingEmailConfirmations)
                .HasForeignKey(d => d.UserId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("pending_email_confirmations_user_id_fkey");
        });

        modelBuilder.Entity<Permiso>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("permisos_pk");

            entity.ToTable("permisos");

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.Activo).HasColumnName("activo");
            entity.Property(e => e.Descripcion)
                .HasColumnType("character varying")
                .HasColumnName("descripcion");
        });

        modelBuilder.Entity<PermisosAccione>(entity =>
        {
            entity
                .HasNoKey()
                .ToTable("permisos_acciones");

            entity.Property(e => e.AccionId).HasColumnName("accion_id");
            entity.Property(e => e.Activo)
                .HasDefaultValue(true)
                .HasColumnName("activo");
            entity.Property(e => e.Id)
                .ValueGeneratedOnAdd()
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.PermisoId).HasColumnName("permiso_id");

            entity.HasOne(d => d.Accion).WithMany()
                .HasForeignKey(d => d.AccionId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("permisos_acciones_acciones_fk");

            entity.HasOne(d => d.Permiso).WithMany()
                .HasForeignKey(d => d.PermisoId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("permisos_acciones_permisos_fk");
        });

        modelBuilder.Entity<PermisosUsuario>(entity =>
        {
            entity
                .HasNoKey()
                .ToView("permisos_usuarios");

            entity.Property(e => e.Accion)
                .HasColumnType("character varying")
                .HasColumnName("accion");
            entity.Property(e => e.AccionId).HasColumnName("accion_id");
            entity.Property(e => e.Activa).HasColumnName("activa");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.PStatus).HasColumnName("p_status");
            entity.Property(e => e.Permiso)
                .HasColumnType("character varying")
                .HasColumnName("permiso");
            entity.Property(e => e.PermisoId).HasColumnName("permiso_id");
            entity.Property(e => e.Usuario).HasColumnName("usuario");
        });

        modelBuilder.Entity<Permisossistema>(entity =>
        {
            entity
                .HasNoKey()
                .ToView("permisossistema");

            entity.Property(e => e.AActiva).HasColumnName("a_activa");
            entity.Property(e => e.Acciondescripcion)
                .HasColumnType("character varying")
                .HasColumnName("acciondescripcion");
            entity.Property(e => e.Accionid).HasColumnName("accionid");
            entity.Property(e => e.PActivo).HasColumnName("p_activo");
            entity.Property(e => e.Permisodescripcion)
                .HasColumnType("character varying")
                .HasColumnName("permisodescripcion");
            entity.Property(e => e.Permisoid).HasColumnName("permisoid");
            entity.Property(e => e.Roledescripcion).HasColumnName("roledescripcion");
            entity.Property(e => e.Roleid).HasColumnName("roleid");
        });

        modelBuilder.Entity<PosicionesEmpledo>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("posiciones_empledos_pkey");

            entity.ToTable("posiciones_empledos");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Nombre).HasColumnName("nombre");
            entity.Property(e => e.TipoEmpleadoId).HasColumnName("tipo_empleado_id");
        });

        modelBuilder.Entity<Provincia>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("provincias_pkey");

            entity.ToTable("provincias");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Nombre).HasColumnName("nombre");
        });

        modelBuilder.Entity<RegistrosEncontrado>(entity =>
        {
            entity
                .HasNoKey()
                .ToTable("registros_encontrados");

            entity.Property(e => e.Count).HasColumnName("count");
        });

        modelBuilder.Entity<Role>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("roles_pkey");

            entity.ToTable("roles");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.Property(e => e.NombreRol).HasColumnName("nombre_rol");
            entity.Property(e => e.UpdatedAt).HasColumnName("updated_at");
        });

        modelBuilder.Entity<RolesPermiso>(entity =>
        {
            entity
                .HasNoKey()
                .ToTable("roles_permisos");

            entity.Property(e => e.Activo)
                .HasDefaultValue(true)
                .HasColumnName("activo");
            entity.Property(e => e.PermisoId).HasColumnName("permiso_id");
            entity.Property(e => e.RoleId).HasColumnName("role_id");

            entity.HasOne(d => d.Permiso).WithMany()
                .HasForeignKey(d => d.PermisoId)
                .HasConstraintName("roles_permisos_permisos_fk");

            entity.HasOne(d => d.Role).WithMany()
                .HasForeignKey(d => d.RoleId)
                .HasConstraintName("roles_permisos_roles_fk");
        });

        modelBuilder.Entity<SeccionesCurso>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("secciones_cursos_pk");

            entity.ToTable("secciones_cursos");

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.Cursoid).HasColumnName("cursoid");
            entity.Property(e => e.Descripcion)
                .HasColumnType("character varying")
                .HasColumnName("descripcion");
            entity.Property(e => e.Responsable).HasColumnName("responsable");

            entity.HasOne(d => d.Curso).WithMany(p => p.SeccionesCursos)
                .HasForeignKey(d => d.Cursoid)
                .HasConstraintName("secciones_cursos_cursos_fk");
        });

        modelBuilder.Entity<Sectore>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("sectores_pkey");

            entity.ToTable("sectores");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CiudadId).HasColumnName("ciudad_id");
            entity.Property(e => e.Nombre).HasColumnName("nombre");

            entity.HasOne(d => d.Ciudad).WithMany(p => p.Sectores)
                .HasForeignKey(d => d.CiudadId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("sectores_ciudad_id_fkey");
        });

        modelBuilder.Entity<Telefono>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("telefonos_pkey");

            entity.ToTable("telefonos");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Numero).HasColumnName("numero");
            entity.Property(e => e.PersonaId).HasColumnName("persona_id");
            entity.Property(e => e.TipoId).HasColumnName("tipo_id");

            entity.HasOne(d => d.Tipo).WithMany(p => p.Telefonos)
                .HasForeignKey(d => d.TipoId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("telefonos_tipo_id_fkey");
        });

        modelBuilder.Entity<TipoContacto>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("tipo_contactos_pkey");

            entity.ToTable("tipo_contactos");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Descripcion).HasColumnName("descripcion");
        });

        modelBuilder.Entity<TipoDireccione>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("tipo_direcciones_pkey");

            entity.ToTable("tipo_direcciones");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Descripcion).HasColumnName("descripcion");
        });

        modelBuilder.Entity<TipoTelefono>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("tipo_telefonos_pkey");

            entity.ToTable("tipo_telefonos");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Descripcion).HasColumnName("descripcion");
        });

        modelBuilder.Entity<TiposEmpledo>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("tipos_empledos_pkey");

            entity.ToTable("tipos_empledos");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Nombre).HasColumnName("nombre");
        });

        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("users_pkey");

            entity.ToTable("users");

            entity.HasIndex(e => e.Email, "users_email_key").IsUnique();

            entity.HasIndex(e => e.Username, "users_username_key").IsUnique();

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.Property(e => e.Email).HasColumnName("email");
            entity.Property(e => e.Fullname).HasColumnName("fullname");
            entity.Property(e => e.Password)
                .HasColumnType("character varying")
                .HasColumnName("password");
            entity.Property(e => e.RoleId).HasColumnName("role_id");
            entity.Property(e => e.UpdatedAt).HasColumnName("updated_at");
            entity.Property(e => e.Username).HasColumnName("username");

            entity.HasOne(d => d.Role).WithMany(p => p.Users)
                .HasForeignKey(d => d.RoleId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("users_role_id_fkey");
        });

        modelBuilder.Entity<UserPermission>(entity =>
        {
            entity
                .HasNoKey()
                .ToView("user_permission");

            entity.Property(e => e.Accion)
                .HasColumnType("character varying")
                .HasColumnName("accion");
            entity.Property(e => e.AccionId).HasColumnName("accion_id");
            entity.Property(e => e.Activa).HasColumnName("activa");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.NombreRol).HasColumnName("nombre_rol");
            entity.Property(e => e.PStatus).HasColumnName("p_status");
            entity.Property(e => e.Permiso)
                .HasColumnType("character varying")
                .HasColumnName("permiso");
            entity.Property(e => e.PermisoId).HasColumnName("permiso_id");
            entity.Property(e => e.RolId).HasColumnName("rol_id");
            entity.Property(e => e.Usuario).HasColumnName("usuario");
        });

        modelBuilder.Entity<UsersCredential>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("users_credentials_pkey");

            entity.ToTable("users_credentials");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.Property(e => e.Password)
                .HasMaxLength(255)
                .HasColumnName("password");
            entity.Property(e => e.UpdatedAt).HasColumnName("updated_at");
            entity.Property(e => e.UserId).HasColumnName("user_id");

            entity.HasOne(d => d.User).WithMany(p => p.UsersCredentials)
                .HasForeignKey(d => d.UserId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("users_credentials_user_id_fkey");
        });

        modelBuilder.Entity<UsuarioPermiso>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("usuario_permisos_pk");

            entity.ToTable("usuario_permisos");

            entity.Property(e => e.Id)
                .UseIdentityAlwaysColumn()
                .HasColumnName("id");
            entity.Property(e => e.AccionId).HasColumnName("accion_id");
            entity.Property(e => e.Activa).HasColumnName("activa");
            entity.Property(e => e.PermisoId).HasColumnName("permiso_id");
            entity.Property(e => e.UserId).HasColumnName("user_id");
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
