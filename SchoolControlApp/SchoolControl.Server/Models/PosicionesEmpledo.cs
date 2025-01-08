using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class PosicionesEmpledo
{
    public int Id { get; set; }

    public string Nombre { get; set; } = null!;

    public string TipoEmpleadoId { get; set; } = null!;
}
