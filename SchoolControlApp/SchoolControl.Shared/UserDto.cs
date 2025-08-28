using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public  class UserDto
    {
        public int Id { get; set; }

        public string? Fullname { get; set; }

        public string? Email { get; set; }

        public string Username { get; set; } = null!;
        public string? Password { get; set; }

        public int? RoleId { get; set; }
        public int docenteID { get; set; }



        public virtual RoleDto? role { get; set; } = new RoleDto();
      
        public override string ToString()
        {
            return $"Id: {Id}, " +
           $"Fullname: {Fullname}, " +
           $"Email: {Email}, " +
           $"Username: {Username}, " +
           $"Password: {(Password != null ? "*****" : "null")}, " +
           $"RoleId: {RoleId}, " +
           $"Role: {(role != null ? role.ToString() : "null")}, "; 
         
        }

    }
}
