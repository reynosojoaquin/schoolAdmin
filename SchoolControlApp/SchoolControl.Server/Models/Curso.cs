using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Curso
{
    public int Cursoid { get; set; }

    public string? Nombre { get; set; }

    public int? Orden { get; set; }

    public virtual ICollection<SeccionesCurso> SeccionesCursos { get; set; } = new List<SeccionesCurso>();
}
