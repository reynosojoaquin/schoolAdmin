using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;


namespace SchoolControl.Shared
{
    public class ResponseApi<T>
    {
        public bool correcto {get;set;}
        public T? Valor { get; set; }

        public string? Mensaje { get; set; }
    }
}
