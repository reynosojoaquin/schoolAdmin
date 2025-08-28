using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Permisossistema
{
    public int? Roleid { get; set; }

    public string? Roledescripcion { get; set; }

    public int? Permisoid { get; set; }

    public string? Permisodescripcion { get; set; }

    public int? Accionid { get; set; }

    public string? Acciondescripcion { get; set; }

    public bool? PActivo { get; set; }

    public bool? AActiva { get; set; }
}
