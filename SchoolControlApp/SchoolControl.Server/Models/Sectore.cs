using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Sectore
{
    public int Id { get; set; }

    public string Nombre { get; set; } = null!;

    public int? CiudadId { get; set; }

    public virtual Ciudade? Ciudad { get; set; }

    public virtual ICollection<Direccione> Direcciones { get; set; } = new List<Direccione>();
}
