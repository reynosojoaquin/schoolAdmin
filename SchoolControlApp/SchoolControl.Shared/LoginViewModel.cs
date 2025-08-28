using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{

   public  class LoginViewModel
    {
        public string UserName { get; set; } = string.Empty;
        [DataType(DataType.Password)]
        public string Password { get; set; } = string.Empty;

        public string Email { get; set; } = string.Empty;
        public string EmailConfirmed { get; set; } = string.Empty;
        public string PasswordConfirmed { get; set; } = string.Empty;
      
    }
}
