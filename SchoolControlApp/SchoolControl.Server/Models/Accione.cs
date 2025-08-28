using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class Accione
{
    public int Id { get; set; }

    public string Descripcion { get; set; } = null!;
}
