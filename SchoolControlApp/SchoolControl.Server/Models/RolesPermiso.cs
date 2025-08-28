using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class RolesPermiso
{
    public int? RoleId { get; set; }

    public int? PermisoId { get; set; }

    public bool? Activo { get; set; }

    public virtual Permiso? Permiso { get; set; }

    public virtual Role? Role { get; set; }
}
