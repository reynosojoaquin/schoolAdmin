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

        public string? Cedula { get; set; } = string.Empty;

        public bool? Activo { get; set; } = false;

        public string? Correo { get; set; } = string.Empty;

        public string? Sexo { get; set; } = string.Empty;

        public string? Url { get; set; } = string.Empty;

        public int? NacionalidadId { get; set; } = 0;

        public string? EstadoCivil { get; set; } = string.Empty;

        public string? Licencia { get; set; } = string.Empty;

        public int? LugarNacimientoId { get; set; } =  0; 

        public string? FechaNacimiento { get; set; } = "2025-08-23";
        public string? SigerdId { get; set; } = string.Empty;
        public int? NumOrden { get; set; } = 0;
        public int  cursoID { get; set; } =  0;
        public bool promovido { get; set; } = false;

        public virtual ICollection<HistoriaClinicaDTO> HistoriasClinicas { get; set; } = new List<HistoriaClinicaDTO>();
        public virtual ICollection<PadresDTO> Padres { get; set; } = new List<PadresDTO>();
        public virtual NacionalidadDTO Nacionalidad { get; set; } = new NacionalidadDTO();
        public virtual LugarNacimientoDTO LugarNacimiento { get; set; } = new LugarNacimientoDTO();
    }
}
