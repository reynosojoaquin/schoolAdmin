using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Security.Claims;
namespace SchoolControl.Shared
{
    public class LoginDto
    {
        public string UserName { get; set; } = string.Empty;
        [DataType(DataType.Password)]
        public string Password { get; set; } = string.Empty;

        public string Email { get; set; } = string.Empty;   
        public string EmailConfirmed { get; set; }     = string.Empty;
        public string PasswordConfirmed { get; set; }  = string.Empty;
     }
}
