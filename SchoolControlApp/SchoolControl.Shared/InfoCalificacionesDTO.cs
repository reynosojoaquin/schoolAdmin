using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class InfoCalificacionesDTO
    {
       public int       estudianteID { get; set; }
       public int       asig_id { get; set; }
       public int       cur_id { get; set; }
       public string?    cur_descripcion { get; set; }
       public string?    asig_descripcion { get; set; }
       public int       comp_id { get; set; }
       public string?    comp_descripcion { get; set; }
       public int       cal_id { get; set; }
       public int       cal_est_id { get; set; }
       public int       cal_asi_comp_id { get; set; }
       public int?       cal_p1 { get; set; }
       public int?       cal_p2 { get; set; }
       public int?       cal_p3 { get; set; }
       public int?       cal_p4 { get; set; }
       public decimal?   cal_final { get; set; }
       public decimal?   cal_rp1 { get; set; }
       public decimal?  cal_rp2 { get; set; }
       public decimal?  cal_rp3 { get; set; }
       public decimal?  cal_rp4 { get; set; }
        public decimal? cal_Pp1 { get; set; }
        public decimal? cal_Pp2 { get; set; }
        public decimal? cal_Pp3 { get; set; }
        public decimal? cal_Pp4 { get; set; }

        public static implicit operator InfoCalificacionesDTO(List<InfoCalificacionesDTO> v)
        {
            throw new NotImplementedException();
        }
    }
}
