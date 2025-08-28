using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;
namespace SchoolControl.Shared
{
    public  class SeccionCursoDTO
    {
        public int Id { get; set; }
       
        public string Descripcion { get; set; } = null!;
       
        public int? CursoId { get; set; }
        public string responsable { get; set; } = null!;



    }
}
