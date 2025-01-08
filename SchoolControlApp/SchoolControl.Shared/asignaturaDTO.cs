using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class asignaturaDTO
    {
        public int id { get; set; }
        public string? Nombre { get; set; }
        public int? CursoID { get; set; }
        public int? responsable { get; set; }

    }
}
