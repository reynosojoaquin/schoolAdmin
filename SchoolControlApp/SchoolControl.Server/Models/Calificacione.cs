using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Calificacione
{
    public int Id { get; set; }

    public int Estudianteid { get; set; }

    public int AsigCompId { get; set; }

    public int? P1 { get; set; }

    public int? P2 { get; set; }

    public int? P3 { get; set; }

    public int? P4 { get; set; }

    public decimal? Final { get; set; }

    public decimal? Rp1 { get; set; }

    public decimal? Rp2 { get; set; }

    public decimal? Rp3 { get; set; }

    public decimal? Rp4 { get; set; }

    public decimal? Pp1 { get; set; }

    public decimal? Pp2 { get; set; }

    public decimal? Pp3 { get; set; }

    public decimal? Pp4 { get; set; }

    public int? CursoId { get; set; }
}
