using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;

namespace SchoolControl.Shared
{
    public class SectorDTO
    {
        public int Id { get; set; }

        public string Nombre { get; set; } = null!;

        public int? CiudadId { get; set; }
        public virtual ICollection<DireccionesDTO> Direcciones { get; set; } = new List<DireccionesDTO>();

    }
}
