using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;
using SchoolControl.Shared.Validators;
namespace SchoolControl.Shared
{
    public  class PadresDTO
    {
        public int Id { get; set; }

        public string Parentesco { get; set; }

        public string? Nombre { get; set; }

        public string? Apellido { get; set; }
        [Required(ErrorMessage = "El teléfono es requerido")]
        [TelefonoValido(ErrorMessage = "El teléfono no es válido")]
        public string? Telefono { get; set; }

        public int? EstudianteId { get; set; }
    }
}
