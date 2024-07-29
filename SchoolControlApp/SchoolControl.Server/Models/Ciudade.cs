using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Ciudade
{
    public int Id { get; set; }

    public string Nombre { get; set; } = null!;

    public int? ProvinciaId { get; set; }

    public virtual ICollection<Direccione> Direcciones { get; set; } = new List<Direccione>();

    public virtual Provincia? Provincia { get; set; }

    public virtual ICollection<Sectore> Sectores { get; set; } = new List<Sectore>();
}
