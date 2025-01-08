using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class CurriculumDetalleDTO
    {
        public int Id { get; set; }

        public string Descripcion { get; set; } = null!;

        public string Fecha { get; set; } = null!;

        public int? CurriculumId { get; set; }

        public bool? Eliminado { get; set; }

        public int? InstitucionId { get; set; }

        public string? UrlFile { get; set; }

        public int? TipoCurriculumId { get; set; }

    }
}
