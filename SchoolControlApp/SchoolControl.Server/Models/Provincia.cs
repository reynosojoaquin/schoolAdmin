using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Provincia
{
    public int Id { get; set; }

    public string Nombre { get; set; } = null!;

    public virtual ICollection<Ciudade> Ciudades { get; set; } = new List<Ciudade>();

    public virtual ICollection<Direccione> Direcciones { get; set; } = new List<Direccione>();
}
