using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Padre
{
    public int Id { get; set; }

    public string? Parentesco { get; set; }

    public string? Nombre { get; set; }

    public string? Apellido { get; set; }

    public string? Telefono { get; set; }

    public int? EstudianteId { get; set; }

    public virtual Estudiante? Estudiante { get; set; }
}
