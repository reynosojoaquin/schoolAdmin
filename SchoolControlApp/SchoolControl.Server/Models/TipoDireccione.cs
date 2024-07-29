using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class TipoDireccione
{
    public int Id { get; set; }

    public string Descripcion { get; set; } = null!;

    public virtual ICollection<Direccione> Direcciones { get; set; } = new List<Direccione>();
}
