using System;
using System.Collections.Generic;

namespace SchoolControl.Server.Models;

public partial class User
{
    public int Id { get; set; }

    public string? Fullname { get; set; }

    public string? Email { get; set; }

    public string Username { get; set; } = null!;

    public DateTime CreatedAt { get; set; }

    public DateTime UpdatedAt { get; set; }

    public int? RoleId { get; set; }

    public virtual ICollection<PendingEmailConfirmation> PendingEmailConfirmations { get; set; } = new List<PendingEmailConfirmation>();

    public virtual Role? Role { get; set; }

    public virtual ICollection<UsersCredential> UsersCredentials { get; set; } = new List<UsersCredential>();
}
