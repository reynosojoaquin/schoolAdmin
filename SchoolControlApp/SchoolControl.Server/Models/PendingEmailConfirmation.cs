﻿using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class PendingEmailConfirmation
{
    public int Id { get; set; }

    public string UniqueCode { get; set; } = null!;

    public DateTime CreatedAt { get; set; }

    public DateTime UpdatedAt { get; set; }

    public int? UserId { get; set; }

    public virtual User? User { get; set; }
}
