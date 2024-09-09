using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;
namespace SchoolControl.Shared
{
public class ProvinciaResponse
{
    public IEnumerable<ProvinciaDTO> Provincias { get; set; } = new List<ProvinciaDTO>();
    public int TotalCount { get; set; }
}
}