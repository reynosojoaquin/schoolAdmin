using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Empleado
{
    public int Id { get; set; }

    public int? PersonaId { get; set; }

    public int TipoEmpleadoId { get; set; }

    public int PosicionId { get; set; }

    public int? TiposEmpledoId { get; set; }

    public int? PosicionesEmpledoId { get; set; }

    public virtual PosicionesEmpledo? PosicionesEmpledo { get; set; }

    public virtual TiposEmpledo? TiposEmpledo { get; set; }
}
