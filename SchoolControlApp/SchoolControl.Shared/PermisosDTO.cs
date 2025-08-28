using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public partial class PermisosDTO
    {
        public int Id { get; set; }

        public string? Descripcion { get; set; }

        public bool? Activo { get; set; }
        public ICollection<AccionesDTO> Acciones { get; set; }
        public List<RolesPermisoDTO> Permisos { get; set; } = new List<RolesPermisoDTO>();
    }
}
