using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class PermisosUsuario
{
    public int? Id { get; set; }

    public string? Permiso { get; set; }

    public string? Accion { get; set; }

    public bool? Activa { get; set; }

    public int? Usuario { get; set; }

    public int? PermisoId { get; set; }

    public int? AccionId { get; set; }

    public bool? PStatus { get; set; }
}
