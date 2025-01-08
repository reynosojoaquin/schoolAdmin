using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class RolesController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public RolesController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<RoleDto>>();
            var ListaRoleDTO = new List<RoleDto>();
            try
            {
                foreach (var item in await _dbContext.Roles.ToListAsync())
                {
                    ListaRoleDTO.Add(new RoleDto
                    {
                        Id = item.Id,
                        NombreRol = item.NombreRol,
                 
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaRoleDTO;
            }
            catch (Exception ex)
            {
                resposeApi.correcto = false;
                resposeApi.Mensaje = ex.Message;
            }
            return Ok(resposeApi);
        }
       
    }
}
