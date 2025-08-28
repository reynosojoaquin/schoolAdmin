using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Security.Policy;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public partial class PermisosSistemaDTO
    {
        public int? id { get; set; }
        public string rolName { get; set; }
        public List<PermisosDTO> Permisos { get; set; }
     
       

    }

}
