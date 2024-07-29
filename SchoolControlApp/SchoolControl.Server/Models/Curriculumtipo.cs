using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Curriculumtipo
{
    public int Id { get; set; }

    public string Descripcion { get; set; } = null!;

    public virtual ICollection<CurriculumDetalle> CurriculumDetalles { get; set; } = new List<CurriculumDetalle>();
}
