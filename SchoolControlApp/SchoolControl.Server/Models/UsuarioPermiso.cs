using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class UsuarioPermiso
{
    public int Id { get; set; }

    public int? PermisoId { get; set; }

    public bool? Activa { get; set; }

    public int? UserId { get; set; }

    public int? AccionId { get; set; }
}
