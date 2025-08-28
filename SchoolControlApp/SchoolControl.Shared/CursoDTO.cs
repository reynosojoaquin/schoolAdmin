
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class CursoDTO
    {
        public int Cursoid { get; set; }

        public string? Nombre { get; set; }

        public int? Responsable { get; set; }
        public int seccionID { get; set; }

        public string? seccion { get; set; }
    }
}
