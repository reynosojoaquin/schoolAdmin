using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class PermisosAccione
{
    public int Id { get; set; }

    public int PermisoId { get; set; }

    public int AccionId { get; set; }

    public bool? Activo { get; set; }

    public virtual Accione Accion { get; set; } = null!;

    public virtual Permiso Permiso { get; set; } = null!;
}
