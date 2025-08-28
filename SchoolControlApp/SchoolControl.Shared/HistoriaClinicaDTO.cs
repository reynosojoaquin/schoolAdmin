using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;
namespace SchoolControl.Shared
{
    public  class HistoriaClinicaDTO
    {
        public int Id { get; set; }
        [Required(ErrorMessage = "Debe seleccionar un tipo la historia clinica")]
        public string? Tipo { get; set; }
        [Required(ErrorMessage ="Debe completar la descripcion de la historia clinica")]
        public string? Descripcion { get; set; }

        public int? EstudianteId { get; set; }
    }
}
