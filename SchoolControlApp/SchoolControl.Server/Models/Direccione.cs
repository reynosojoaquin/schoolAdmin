using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Direccione
{
    public int Id { get; set; }

    public string Calle { get; set; } = null!;

    public string Numero { get; set; } = null!;

    public string? Apartamento { get; set; }

    public string? Longitud { get; set; }

    public string? Latitude { get; set; }

    public int? PersonaId { get; set; }

    public int? TipoId { get; set; }

    public int? ProvinciaId { get; set; }

    public int? CiudadId { get; set; }

    public int? SectorId { get; set; }

    public virtual Ciudade? Ciudad { get; set; }

    public virtual Provincia? Provincia { get; set; }

    public virtual Sectore? Sector { get; set; }

    public virtual TipoDireccione? Tipo { get; set; }
}
