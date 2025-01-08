using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class EstudiantesDTO
    {
        public int Id { get; set; }

        public string Nombres { get; set; } = null!;

        public string Apellidos { get; set; } = null!;

        public string Cedula { get; set; } = null!;

        public bool? Activo { get; set; }

        public string? Correo { get; set; }

        public string? Sexo { get; set; }

        public string? Url { get; set; }

        public int? NacionalidadId { get; set; }

        public string? EstadoCivil { get; set; }

        public string? Licencia { get; set; }

        public int? LugarNacimientoId { get; set; }

        public string? FechaNacimiento { get; set; }

      
    }
}
