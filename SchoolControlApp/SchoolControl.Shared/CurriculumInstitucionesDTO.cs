using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    internal class CurriculumInstitucionesDTO
    {
        public int Id { get; set; }

        public string Descripcion { get; set; } = null!;

        public int? Eliminado { get; set; }

        public virtual ICollection<CurriculumDetalleDTO> CurriculumDetalles { get; set; } = new List<CurriculumDetalleDTO>();
    }
}
