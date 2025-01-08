using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    internal class NacionalidadDTO
    {
        public int Id { get; set; }

        public string Nombre { get; set; } = null!;

        public int? NacionalidadId { get; set; }

        public virtual ICollection<DocenteDTO> Docentes { get; set; } = new List<DocenteDTO>();

        public virtual ICollection<EstudiantesDTO> Estudiantes { get; set; } = new List<EstudiantesDTO>();
    }
}
