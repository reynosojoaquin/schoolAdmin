using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Nacionalidade
{
    public int Id { get; set; }

    public string Nombre { get; set; } = null!;

    public string? Cod { get; set; }

    public virtual ICollection<Docente> Docentes { get; set; } = new List<Docente>();

    public virtual ICollection<Estudiante> Estudiantes { get; set; } = new List<Estudiante>();
}
