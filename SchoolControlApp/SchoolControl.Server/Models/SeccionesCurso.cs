using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class SeccionesCurso
{
    public int Id { get; set; }

    public string? Descripcion { get; set; }

    public int? Cursoid { get; set; }

    public int? Responsable { get; set; }

    public virtual Curso? Curso { get; set; }
}
