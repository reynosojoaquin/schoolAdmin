using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Curriculum
{
    public int Id { get; set; }

    public int EmpleadoId { get; set; }

    public string? CarpetasCurriculum { get; set; }

    public virtual ICollection<CurriculumDetalle> CurriculumDetalles { get; set; } = new List<CurriculumDetalle>();
}
