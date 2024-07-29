using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class TipoTelefono
{
    public int Id { get; set; }

    public string Descripcion { get; set; } = null!;

    public virtual ICollection<Telefono> Telefonos { get; set; } = new List<Telefono>();
}
