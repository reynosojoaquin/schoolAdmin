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

    public virtual DbSet<Ciudade> Ciudades { get; set; }

    public virtual DbSet<Contacto> Contactos { get; set; }

    public virtual DbSet<Curriculum> Curricula { get; set; }

    public virtual DbSet<CurriculumDetalle> CurriculumDetalles { get; set; }

    public virtual DbSet<CurriculumInstitucione> CurriculumInstituciones { get; set; }

    public virtual DbSet<Curriculumtipo> Curriculumtipos { get; set; }

    public virtual DbSet<Direccione> Direcciones { get; set; }

    public virtual DbSet<Empleado> Empleados { get; set; }

    public virtual DbSet<LugarNacimiento> LugarNacimientos { get; set; }

    public virtual DbSet<Nacionalidade> Nacionalidades { get; set; }

    public virtual DbSet<PendingEmailConfirmation> PendingEmailConfirmations { get; set; }

    public virtual DbSet<Persona> Personas { get; set; }

    public virtual DbSet<PosicionesEmpledo> PosicionesEmpledos { get; set; }

    public virtual DbSet<Provincia> Provincias { get; set; }

    public virtual DbSet<Role> Roles { get; set; }

    public virtual DbSet<Sectore> Sectores { get; set; }

    public virtual DbSet<Telefono> Telefonos { get; set; }

    public virtual DbSet<TipoContacto> TipoContactos { get; set; }

    public virtual DbSet<TipoDireccione> TipoDirecciones { get; set; }

    public virtual DbSet<TipoTelefono> TipoTelefonos { get; set; }

    public virtual DbSet<TiposEmpledo> TiposEmpledos { get; set; }

    public virtual DbSet<User> Users { get; set; }

    public virtual DbSet<UsersCredential> UsersCredentials { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
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

        modelBuilder.Entity<Empleado>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("empleados_pkey");

            entity.ToTable("empleados");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.PersonaId).HasColumnName("persona_id");
            entity.Property(e => e.PosicionId).HasColumnName("posicion_id");
            entity.Property(e => e.PosicionesEmpledoId).HasColumnName("posiciones_empledo_id");
            entity.Property(e => e.TipoEmpleadoId).HasColumnName("tipo_empleado_id");
            entity.Property(e => e.TiposEmpledoId).HasColumnName("tipos_empledo_id");

            entity.HasOne(d => d.PosicionesEmpledo).WithMany(p => p.Empleados)
                .HasForeignKey(d => d.PosicionesEmpledoId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("empleados_posiciones_empledo_id_fkey");

            entity.HasOne(d => d.TiposEmpledo).WithMany(p => p.Empleados)
                .HasForeignKey(d => d.TiposEmpledoId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("empleados_tipos_empledo_id_fkey");
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
            entity.Property(e => e.NacionalidadId).HasColumnName("nacionalidad_id");
            entity.Property(e => e.Nombre).HasColumnName("nombre");
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

        modelBuilder.Entity<Persona>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("personas_pkey");

            entity.ToTable("personas");

            entity.HasIndex(e => e.Cedula, "personas_cedula_key").IsUnique();

            entity.Property(e => e.Id).HasColumnName("id");
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

            entity.HasOne(d => d.LugarNacimiento).WithMany(p => p.Personas)
                .HasForeignKey(d => d.LugarNacimientoId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("personas_lugar_nacimiento_id_fkey");

            entity.HasOne(d => d.Nacionalidad).WithMany(p => p.Personas)
                .HasForeignKey(d => d.NacionalidadId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("personas_nacionalidad_id_fkey");
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

        modelBuilder.Entity<Role>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("roles_pkey");

            entity.ToTable("roles");

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.Property(e => e.NombreRol).HasColumnName("nombre_rol");
            entity.Property(e => e.UpdatedAt).HasColumnName("updated_at");
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
            entity.Property(e => e.RoleId).HasColumnName("role_id");
            entity.Property(e => e.UpdatedAt).HasColumnName("updated_at");
            entity.Property(e => e.Username).HasColumnName("username");

            entity.HasOne(d => d.Role).WithMany(p => p.Users)
                .HasForeignKey(d => d.RoleId)
                .OnDelete(DeleteBehavior.SetNull)
                .HasConstraintName("users_role_id_fkey");
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

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
