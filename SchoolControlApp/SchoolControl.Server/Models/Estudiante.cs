using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Estudiante
{
    public int Id { get; set; }

    public string Nombres { get; set; } = null!;

    public string Apellidos { get; set; } = null!;

    public string? Cedula { get; set; }

    public bool? Activo { get; set; }

    public string? Correo { get; set; }

    public string? Sexo { get; set; }

    public string? Url { get; set; }

    public int? NacionalidadId { get; set; }

    public string? EstadoCivil { get; set; }

    public string? Licencia { get; set; }

    public int? LugarNacimientoId { get; set; }

    public string? FechaNacimiento { get; set; }

    public int? Cursoid { get; set; }

    public int? NumOrden { get; set; }

    public string? SigerdId { get; set; }

    public bool? Promovido { get; set; }

    public bool? Esnuevoingreso { get; set; }

    public virtual ICollection<HistoriaClinica> HistoriaClinicas { get; set; } = new List<HistoriaClinica>();

    public virtual LugarNacimiento? LugarNacimiento { get; set; }

    public virtual Nacionalidade? Nacionalidad { get; set; }

    public virtual ICollection<Padre> Padres { get; set; } = new List<Padre>();
}
