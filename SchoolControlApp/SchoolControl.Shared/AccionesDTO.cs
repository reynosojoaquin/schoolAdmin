using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public partial class AccionesDTO
    {

        public int? id { get; set; }
        public string? Descripcion { get; set; }
        public Boolean? Activa { get; set; } = true;
        public virtual ICollection<PermisosAccione> PermisosAcciones { get; set; }  = new List<PermisosAccione>();  
    }
}
