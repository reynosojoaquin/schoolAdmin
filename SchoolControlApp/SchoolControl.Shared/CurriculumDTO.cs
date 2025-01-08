using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    internal class CurriculumDTO
    {
        public int Id { get; set; }

        public int EmpleadoId { get; set; }

        public string? CarpetasCurriculum { get; set; }

        public virtual ICollection<CurriculumDetalleDTO> CurriculumDetalles { get; set; } = new List<CurriculumDetalleDTO>();
    }
}
