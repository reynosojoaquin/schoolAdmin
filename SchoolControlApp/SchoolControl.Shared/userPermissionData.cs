using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class userPermissionData
    {
        public string role { get; set; }
        public int permisoID { get; set; }
        public string permiso { get; set; }
        public int accionID { get; set; }
        public string accion { get; set; }
        public bool A_status { get; set; }
        public bool P_status { get; set; }
    }

}
