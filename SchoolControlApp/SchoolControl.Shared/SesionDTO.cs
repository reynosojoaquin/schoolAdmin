using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class SesionDTO
    {
        public string userName { get; set; } = string.Empty;
        public string Correo { get; set; } = string.Empty;
        public string Rol { get; set; } = string.Empty; 
        public string token {  get; set; } = string.Empty;
        public string fullName { get; set; } = string.Empty;
        public Dictionary<string, string> CustomClaims { get; set; }
        public int Id { get; set; } = 0;
    }
}
