using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Asignatura
{
    public int Id { get; set; }

    public string? Nombre { get; set; }

    public int? Cursoid { get; set; }

    public int? Responsable { get; set; }
}
