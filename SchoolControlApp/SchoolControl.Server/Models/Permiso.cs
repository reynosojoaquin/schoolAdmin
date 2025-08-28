using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Permiso
{
    public int Id { get; set; }

    public string? Descripcion { get; set; }

    public bool? Activo { get; set; }
}
