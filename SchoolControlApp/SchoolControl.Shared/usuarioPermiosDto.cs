using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public partial class UsuarioPermisosDTO
    {
        public int Id { get; set; }

        public int? AccionId { get; set; }

        public bool? Activa { get; set; }
        public int? UserId { get; set; }
        AccionesDTO Acciones { get; set; }  = new AccionesDTO();
    }

}
