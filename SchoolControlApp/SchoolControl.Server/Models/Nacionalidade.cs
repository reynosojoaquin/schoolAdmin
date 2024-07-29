using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Nacionalidade
{
    public int Id { get; set; }

    public string Nombre { get; set; } = null!;

    public int? NacionalidadId { get; set; }

    public virtual ICollection<Persona> Personas { get; set; } = new List<Persona>();
}
