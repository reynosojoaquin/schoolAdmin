using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class TipoContacto
{
    public int Id { get; set; }

    public string Descripcion { get; set; } = null!;

    public virtual ICollection<Contacto> Contactos { get; set; } = new List<Contacto>();
}
