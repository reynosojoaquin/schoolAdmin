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
        [HttpPut]
        [Route("updateSystemPermmisions/{id}")]

        public async Task<IActionResult> updateSystemPermmisions(PermisosSistemaDTO permisos)
        {

            var responseApi = new ResponseApi<int>();

            try
            {
                 
                 foreach( var permiso in  permisos.Permisos)
                {
                    RolesPermiso permisoDB = await _dbContext.RolesPermisos.Where(rp => 
                    rp.RoleId == permisos.id && rp.PermisoId == permiso.Id).FirstOrDefaultAsync();
                    if (permisoDB != null) { 
                        permisoDB.Activo = permiso.Activo;
                    }
                    foreach(var accion in permiso.Acciones)
                    {
                        var accionDb = await _dbContext.PermisosAcciones
                            .Where(a => a.AccionId == accion.id && a.PermisoId == permiso.Id).FirstOrDefaultAsync();
                        if (accionDb != null) {
                            accionDb.Activo = accion.Activa;
                        }
                        _dbContext.SaveChanges();
                    }
                } 

                responseApi.correcto = true;
                responseApi.Valor = 1;
             }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }
    }
}
