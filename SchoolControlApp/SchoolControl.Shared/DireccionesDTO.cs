using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;

namespace SchoolControl.Shared
{
    public class DireccionesDTO
    {
        public int Id { get; set; }

        public string Calle { get; set; } = null!;

        public string Numero { get; set; } = null!;

        public string? Apartamento { get; set; }

        public string? Longitud { get; set; }

        public string? Latitude { get; set; }

        [Required]
        public int? PersonaId { get; set; }

        public int? TipoId { get; set; }

        public int? ProvinciaId { get; set; }

        public int? CiudadId { get; set; }

        public int? SectorId { get; set; }
        public virtual CiudadDTO? Ciudad { get; set; }

        public virtual ProvinciaDTO? Provincia { get; set; }

        public virtual SectorDTO? Sector { get; set; }

        public virtual TipoDireccionDTO? Tipo { get; set; }


    }
}
