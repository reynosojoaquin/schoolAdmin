using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public partial class PermisosAccione
    {
        public int Id { get; set; }

        public int? accionID { get; set; }

        public int PermisoId { get; set; }
        public PermisosDTO PermisosDTO { get; set; } = new PermisosDTO();   
        public AccionesDTO AccionesDTO { get; set; } = new AccionesDTO();
    }


}

