using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;
namespace SchoolControl.Shared
{
    public class TipoDireccionDTO
    {
        public int Id { get; set; }
        [Required(ErrorMessage ="Este campo {0} es requerido.")]
        public string Descripcion { get; set; } = null!;
        public virtual ICollection<DireccionesDTO> Direcciones { get; set; } = new List<DireccionesDTO>();

    }
}
