using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Asignaturacompetencia
{
    public int Id { get; set; }

    public int Asignaturaid { get; set; }

    public int Competenciaid { get; set; }
}
