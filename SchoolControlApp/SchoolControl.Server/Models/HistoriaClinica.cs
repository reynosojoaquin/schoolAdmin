using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class HistoriaClinica
{
    public int Id { get; set; }

    public string? Tipo { get; set; }

    public string? Descripcion { get; set; }

    public int? EstudianteId { get; set; }

    public virtual Estudiante? Estudiante { get; set; }
}
