using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Contacto
{
    public int Id { get; set; }

    public int? PersonaId { get; set; }

    public string Nombre { get; set; } = null!;

    public string Apellido { get; set; } = null!;

    public string Telefono { get; set; } = null!;

    public string? Direccion { get; set; }

    public int? TipoId { get; set; }

    public virtual TipoContacto? Tipo { get; set; }
}
