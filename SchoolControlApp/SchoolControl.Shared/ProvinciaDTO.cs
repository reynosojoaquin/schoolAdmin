using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;
namespace SchoolControl.Shared
{
    public class ProvinciaDTO
    {
        public int Id { get; set; }

        [Required]
        public string Nombre { get; set; } = null!;
        public virtual ICollection<CiudadDTO> Ciudades { get; set; } = new List<CiudadDTO>();

        public virtual ICollection<DireccionesDTO> Direcciones { get; set; } = new List<DireccionesDTO>();


    }
}
