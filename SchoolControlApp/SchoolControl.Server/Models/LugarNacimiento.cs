using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class LugarNacimiento
{
    public int Id { get; set; }

    public string Nombre { get; set; } = null!;

    public int? LugarNacimientoId { get; set; }

    public virtual ICollection<Persona> Personas { get; set; } = new List<Persona>();
}
