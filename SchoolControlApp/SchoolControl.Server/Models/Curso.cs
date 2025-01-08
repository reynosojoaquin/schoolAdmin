using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Curso
{
    public int Cursoid { get; set; }

    public string? Nombre { get; set; }

    public int? Responsable { get; set; }
}
