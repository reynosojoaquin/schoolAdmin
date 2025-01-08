using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class CalificacionesDTO
    {
        public int Id { get; set; }

        public int Estudianteid { get; set; }

        public int Asigcompid { get; set; }

        public int? P1 { get; set; }

        public int? P2 { get; set; }

        public int? P3 { get; set; }

        public int? P4 { get; set; }
        public decimal? cal_final { get; set; }
        public decimal? cal_rp1 { get; set; }
        public decimal? cal_rp2 { get; set; }
        public decimal? cal_rp3 { get; set; }
        public decimal? cal_rp4 { get; set; }
        public decimal? cal_Pp1 { get; set; }
        public decimal? cal_Pp2 { get; set; }
        public decimal? cal_Pp3 { get; set; }
        public decimal? cal_Pp4 { get; set; }
    }
}
