using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public partial class RolesPermisoDTO
    {
        public int? RoleId { get; set; }
        RoleDto roleDto { get; set; } = new RoleDto();
        public int? PermisoId { get; set; }
        PermisosDTO permisosDto { get; set; } = new PermisosDTO();
    }

}
