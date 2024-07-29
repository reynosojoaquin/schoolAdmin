using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class TiposEmpledo
{
    public int Id { get; set; }

    public string Nombre { get; set; } = null!;

    public virtual ICollection<Empleado> Empleados { get; set; } = new List<Empleado>();
}
