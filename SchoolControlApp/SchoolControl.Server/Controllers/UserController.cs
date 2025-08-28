using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using System.IdentityModel.Tokens.Jwt;
using System.Runtime.InteropServices;
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

        public UserController(SchoolControlDbContext dbcontext, IConfiguration configuration)
        {
            _dbContext = dbcontext;
            _configuration = configuration;

        }
        [AllowAnonymous]
        [HttpPost]
        [Route("Login")]
        public async Task<IActionResult> Login(LoginViewModel login)
        {
            var respose = new ResponseApi<SesionDTO>();
            var sesion = new SesionDTO();
            string userToken = string.Empty;
            int docenteID = 0;

            if (login.UserName == "admin" && login.Password == "admin")
            {
                sesion.userName = "admin";
                sesion.Correo = login.Email ?? "admin@default.com";
                sesion.Rol = "Administrador";
                sesion.token = await GenerateToken(new UserDto { Email = sesion.Correo, RoleId = 1 });
                sesion.fullName = "Administrador";

                respose.Valor = sesion;
                respose.Mensaje = "Usuario admin logeado con éxito";
                respose.correcto = true;

                return Ok(respose);
            }

            var user = await _dbContext.Users.Include(c => c.Role).FirstOrDefaultAsync(u => u.Username == login.UserName);
            if (user != null && user.Password == login.Password)
            {
                if(user.Role.NombreRol == "Docente")
                {
                    docenteID = (await _dbContext.Docentes.FirstOrDefaultAsync(d => d.Userid == user.Id))?.Id ?? 0; 
                }
                var currentUser = new UserDto
                {
                    Email = user.Email,
                    Fullname = user.Fullname,
                    Id = docenteID,
                    RoleId = user.RoleId,
                    role = user.Role != null ? new RoleDto
                    {
                        Id = user.Role.Id,
                        NombreRol = user.Role.NombreRol,
                    } : null
                };

                userToken = await GenerateToken(currentUser);
                sesion.userName = user.Username;
                sesion.Correo = user.Email;
                sesion.Rol = currentUser.role?.NombreRol ?? "Sin Rol";
                sesion.token = userToken;
                sesion.fullName = user.Fullname;
                sesion.Id = currentUser.Id;
                respose.Mensaje = "Usuario logeado con éxito";
                respose.correcto = true;
                sesion.CustomClaims = await GenerateCustomClaim(user.Id);
                respose.Valor = sesion;
                return Ok(respose);
            }
            respose.Mensaje = "Error en el nombre de usuario o la contraseña";
            respose.Valor = null;
            respose.correcto = false;
            return BadRequest(respose);
        }

        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<UserDto>>();
            var ListaUserDTO = new List<UserDto>();
            try
            {
                foreach (var item in await _dbContext.Users.Include(u => u.Role).ToListAsync())
                {
                    ListaUserDTO.Add(new UserDto
                    {
                        Id = item.Id,
                        Username = item.Username,
                        Email = item.Email,
                        Password = item.Password,
                        RoleId = item.RoleId,
                        Fullname = item.Fullname,
                        role = new RoleDto
                        {
                            Id = item.Role.Id,
                            NombreRol = item.Role.NombreRol

                        }
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaUserDTO;
            }
            catch (Exception ex)
            {
                resposeApi.correcto = false;
                resposeApi.Mensaje = ex.Message;
            }
            return Ok(resposeApi);
        }
        private async Task<string> GenerateToken(UserDto user)
        {
          //  List<PermisosSistemaDTO> permisos = GetUserPermmissionAsync(user.Id).Result.Valor;

            var claims = new List<Claim>();
            Dictionary<string, string> claimData = new Dictionary<string, string>();
            claimData = await GenerateCustomClaim(user.Id);
            foreach (var item in claimData)
            {
                claims.Add(new Claim(item.Key, item.Value));
            }   
            if (claims != null)
            {
                var jwtHandler = new JwtSecurityTokenHandler();
                var response = new ResponseApi<string>();
                var audience = _configuration["Jwt:JWT_AUDIENCE"];
                var issue = _configuration["Jwt:JWT_ISSUER"];
                var jwtkey = _configuration["Jwt:JWT_KEY"];
                double.TryParse(_configuration["Jwt:JWT_EXPIRATION_TIME"], out var expiration);

                var symmetricSecurityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtkey));
                var signingCredentials = new SigningCredentials(symmetricSecurityKey, SecurityAlgorithms.HmacSha256);
                var expireTime = DateTime.UtcNow.AddMinutes(expiration);
                claims.Add(new Claim(JwtRegisteredClaimNames.Sub, user.Fullname!));
                claims.Add(new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()));
                claims.Add(new Claim(JwtRegisteredClaimNames.Email, user.Email!));
                ClaimsIdentity claimsIdentity = new ClaimsIdentity(claims);
                var tokenDescriptor = new SecurityTokenDescriptor
                {

                    Subject = claimsIdentity,
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
            return string.Empty;


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
                    RoleId = User.RoleId,
                    Fullname = User.Fullname,
                    CreatedAt = DateTime.Now.ToUniversalTime()

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
        [HttpGet]
        [Route("getSystemPermission")]

        public async Task<IActionResult> getSystemPermission()
        {
            var responseApi = new ResponseApi<List<PermisosSistemaDTO>>();
            List<PermisosSistemaDTO> permisosSistemaDTO = new List<PermisosSistemaDTO>();
            try
            {

                var permisos = await _dbContext.Permisossistemas.ToListAsync();

                permisosSistemaDTO = permisos
                .GroupBy(p => new { p.Roleid, p.Roledescripcion })
                .Select(grp => new PermisosSistemaDTO
                {
                    id = grp.Key.Roleid,
                    rolName = grp.Key.Roledescripcion,
                    Permisos = grp.GroupBy(p => new { p.Permisoid, p.Permisodescripcion, p.PActivo })
                                  .Select(gp => new PermisosDTO
                                  {
                                      Id = gp.Key.Permisoid.GetValueOrDefault(),
                                      Descripcion = gp.Key.Permisodescripcion,
                                      Activo = gp.Key.PActivo,
                                      Acciones = gp.Select(a => new AccionesDTO
                                      {
                                          id = a.Accionid,
                                          Descripcion = a.Acciondescripcion,
                                          Activa = a.AActiva

                                      }).Distinct().ToList()
                                  }).ToList()
                }).ToList();
                responseApi.correcto = true;
                responseApi.Valor = permisosSistemaDTO;
                return Ok(responseApi);
            }
            catch (Exception ex)
            {

                return StatusCode(StatusCodes.Status500InternalServerError, $"Error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetUserPermissionAsync/{userID}")]
        public async Task<ResponseApi<List<PermisosSistemaDTO>>> GetUserPermmissionAsync(int userID)
        {
            var responseApi = new ResponseApi<List<PermisosSistemaDTO>>();
            List<UserPermission> _permisos = new List<UserPermission>();

            try
            {
                if (userID <= 0)
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "El ID de usuario no es válido.";
                    return responseApi;
                }
                _permisos = await getUserPermission(userID);

                if (_permisos == null || !_permisos.Any())
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "No se encontraron permisos para el usuario.";
                    return responseApi;
                }


                var permisosSistemaDTO = _permisos
                .GroupBy(p => new { p.RolId, p.NombreRol })
                .Select(grp => new PermisosSistemaDTO
                {
                    id = grp.Key.RolId,
                    rolName = grp.Key.NombreRol,
                    Permisos = grp.GroupBy(p => new { p.PermisoId, p.Permiso, p.PStatus })
                                  .Select(gp => new PermisosDTO
                                  {
                                      Id = gp.Key.PermisoId.GetValueOrDefault(),
                                      Descripcion = gp.Key.Permiso,
                                      Activo = gp.Key.PStatus,
                                      Acciones = gp.Select(a => new AccionesDTO
                                      {
                                          id = a.AccionId,
                                          Descripcion = a.Accion,
                                          Activa = a.Activa

                                      }).ToList()
                                  }).ToList()
                }).ToList();
                responseApi.correcto = true;
                responseApi.Valor = permisosSistemaDTO;
                responseApi.Mensaje = "Permisos encontrados.";

                return responseApi;
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = $"Error interno: {ex.Message}";
                return responseApi;
            }
        }


        [HttpGet]
        [Route("getUserPermission")]
        public async Task<List<UserPermission>> getUserPermission(int id)
        {
            List<UserPermission> permission = new List<UserPermission>();
            /* var permisosPorRol = await (
                    from _roles in _dbContext.Roles
                    join rp in _dbContext.RolesPermisos on _roles.Id equals rp.RoleId
                    join p in _dbContext.Permisos on rp.PermisoId equals p.Id
                    join _users in _dbContext.Users on _roles.Id equals _users.RoleId
                    join pa in _dbContext.PermisosAcciones on p.Id equals pa.PermisoId
                    join _acciones in _dbContext.Acciones on pa.AccionId equals _acciones.Id
                    where _users.Id == id
                    select new userPermissionData
                    {
                        role = _roles.NombreRol,
                        permiso = p.Descripcion,
                        accion = _acciones.Descripcion,
                        A_status = pa.Activo.GetValueOrDefault(),
                        permisoID = p.Id,
                        accionID = _acciones.Id,
                        P_status = rp.Activo.GetValueOrDefault(),
                    }
                ).ToListAsync(); */


            try
            {

                permission = await _dbContext.UserPermissions.Where(c => c.Usuario == id).ToListAsync();
                return permission;
            }
            catch (Exception ex)
            {

                return permission;
            }

        }

        [HttpGet]
        [Route("GenerateCustomClaim")]
        public async Task<Dictionary<string,string>> GenerateCustomClaim(int userID)
        {
            var response = await GetUserPermmissionAsync(userID);
            List<PermisosSistemaDTO> permisos = response?.Valor ?? new List<PermisosSistemaDTO>();
            Dictionary<string, string> claims = new Dictionary<string, string>();

            if (permisos.Count > 0)
            {
                foreach (var rol in permisos)
                {
                    foreach (var permiso in rol.Permisos ?? new List<PermisosDTO>())
                    {
                        string opcion = $"{permiso.Descripcion}.{permiso.Activo}";
                        claims.Add($"Permission.{permiso.Id}", opcion);
                        foreach (var a in permiso.Acciones ?? new List<AccionesDTO>())
                        {
                            string accion = $"{permiso.Descripcion}.{a.Descripcion}.{a.Activa}";
                            claims.Add($"accion.{permiso.Id}.{a.id}", accion);
                        }
                    }
                }
            }

            return claims;
        }
    }

}
