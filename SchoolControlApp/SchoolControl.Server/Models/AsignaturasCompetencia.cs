using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class AsignaturasCompetencia
{
    public int Id { get; set; }

    public int Competenciaid { get; set; }

    public int? Cursoid { get; set; }

    public int Asignaturaid { get; set; }
}
