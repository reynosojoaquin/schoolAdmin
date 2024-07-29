using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Telefono
{
    public int Id { get; set; }

    public string Numero { get; set; } = null!;

    public int? PersonaId { get; set; }

    public int? TipoId { get; set; }

    public virtual TipoTelefono? Tipo { get; set; }
}
