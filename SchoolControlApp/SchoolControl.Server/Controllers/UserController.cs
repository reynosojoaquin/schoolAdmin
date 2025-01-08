using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class UserController : Controller
    {
        private readonly SchoolControlDbContext _dbContext;
       
        private readonly IConfiguration _configuration;




        public UserController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
           
           
        }
        [AllowAnonymous]
        [HttpPost]
        [Route("Login")]
        public async Task<IActionResult> Login(LoginDto login)
            {
             SesionDTO sesion = new SesionDTO();
            string userToken = string.Empty;  
            var respose = new ResponseApi<SesionDTO>();
            if (login.UserName == "admin" && login.Password == "admin")
            {
                sesion.userName = "admin";
                sesion.Correo = login.Email;
                sesion.Rol = "Administrador";
                respose.Valor = sesion;
                return  Ok(respose);

            }
          
            var user = await _dbContext.Users.FirstOrDefaultAsync(u => u.Username == login.UserName);
            if (user != null)
            {
                 UserDto currentUser =  new UserDto 
                            {  
                                Email = user.Email,
                                Fullname = user.Fullname,
                                Id = user.Id,
                                RoleId = user.RoleId,   
                                role = new RoleDto
                                {
                                    Id = user.Role.Id,
                                    NombreRol = user.Role.NombreRol,
                                }
            
                            };
              
                /*   if (login.Email == "admin@rtfd.com" && login.Password == "admin") { 
                           sesion.userName = "admin";
                           sesion.Correo = login.Email;
                           sesion.Rol = "Administrador";
                   }
                   else{
                       sesion.userName = "empleado";
                       sesion.Correo = login.Email;
                       sesion.Rol = "Empleado";
                       }*/


               
                if (currentUser != null)
                {
                    userToken = await GenerateToken(currentUser);
                    sesion.userName = user.Username;
                    sesion.Correo = user.Email;
                    sesion.Rol = currentUser.role.NombreRol;
                    sesion.token = userToken;

                }
                else
                {
                    respose.Mensaje = "Error en el nombre de usuario";
                    respose.Valor = null;
                }


            }
            else
            {
                respose.Mensaje = "Error en el nombre de usuario o la contraseña";
                respose.Valor = null;
            }







            return Ok(respose);
        }
        private async Task<string> GenerateToken(UserDto user)
        {
            var jwtHandler = new JwtSecurityTokenHandler();
            var response = new ResponseApi<string>();
            var audience = _configuration["JWT_AUDIENCE"];
            var issue = _configuration["JWT_ISSUER"];
            var jwtkey = _configuration["JWT_KEY"];
            double.TryParse(_configuration["JWT_EXPIRATION_TIME"], out var expiration);

            var symmetricSecurityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtkey));
            var signingCredentials = new SigningCredentials(symmetricSecurityKey, SecurityAlgorithms.HmacSha256);
            var expireTime = DateTime.UtcNow.AddMinutes(expiration);


            var tokenDescriptor = new SecurityTokenDescriptor
            {
              
                Subject = new ClaimsIdentity(new[] {
                 new Claim(JwtRegisteredClaimNames.Sub, user.Fullname!),
                 new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
                 new Claim(JwtRegisteredClaimNames.Email, user.Email!),
                }),
                Audience = audience,
                Issuer = issue,
                Expires = expireTime,
                SigningCredentials = signingCredentials
            };

            try
            { 
                var token = jwtHandler.CreateToken(tokenDescriptor);
                var jwtToken = jwtHandler.WriteToken(token);
               
              
                return jwtToken;
            }
            catch (Exception ex)
            {
                response.Valor = null;  
                response.correcto = false;
                response.Mensaje = "Error generando el token";
                return string.Empty;
            }
        }

        [HttpPut]
        [Route("Editar/{id}")]
        public async Task<IActionResult> Editar(UserDto user, int id)
        {

            var responseApi = new ResponseApi<int>();

            try
            {
                var DBUser = await _dbContext.Users.FirstOrDefaultAsync(x => x.Id == id);

                if (DBUser != null)
                {
                    DBUser.Password = user.Password;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBUser.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Usuario no encontrado";
                }

            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPost]
        [Route("Guardar")]

        public async Task<IActionResult> Guardar(UserDto User)
        {
           
            var responseApi = new ResponseApi<int>();
          
            using var transaction = await _dbContext.Database.BeginTransactionAsync();
            try
            {
                Docente _docente = await _dbContext.Docentes.FirstOrDefaultAsync(d => d.Id == User.docenteID);
               
                var DBUser = new User
                {
                    Username = User.Username,
                    Email = User.Email,
                    Password = User.Password,
                    RoleId   = User.RoleId,
                    Fullname = User.Fullname,
                    CreatedAt = DateTime.Now
                    
                };
                _dbContext.Users.Add(DBUser);
                await _dbContext.SaveChangesAsync();
                if (DBUser.Id != 0)
                {
                    _docente.Userid = DBUser.Id;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBUser.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Error registrado el usuario";
                }
                await transaction.CommitAsync();
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                if (ex.InnerException != null)
                {
                    responseApi.Mensaje = ex.InnerException.Message;
                }
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }
    }
}
