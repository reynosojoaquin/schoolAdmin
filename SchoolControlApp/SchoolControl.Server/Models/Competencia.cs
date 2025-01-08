using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Competencia
{
    public int Id { get; set; }

    public string Descripcion { get; set; } = null!;
}
