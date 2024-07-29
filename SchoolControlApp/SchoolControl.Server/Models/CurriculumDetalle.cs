using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class CurriculumDetalle
{
    public int Id { get; set; }

    public string Descripcion { get; set; } = null!;

    public string Fecha { get; set; } = null!;

    public int? CurriculumId { get; set; }

    public bool? Eliminado { get; set; }

    public int? InstitucionId { get; set; }

    public string? UrlFile { get; set; }

    public int? TipoCurriculumId { get; set; }

    public virtual Curriculum? Curriculum { get; set; }

    public virtual CurriculumInstitucione? Institucion { get; set; }

    public virtual Curriculumtipo? TipoCurriculum { get; set; }
}
