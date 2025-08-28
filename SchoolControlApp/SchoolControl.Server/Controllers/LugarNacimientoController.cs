using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class LugarNacimientoController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public LugarNacimientoController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<LugarNacimientoDTO>>();
            var ListaLugarNacimientoDTO = new List<LugarNacimientoDTO>();
            try
            {
                foreach (var item in await _dbContext.LugarNacimientos.ToListAsync())
                {
                    ListaLugarNacimientoDTO.Add(new LugarNacimientoDTO
                    {
                        Id          = item.Id,
                        Nombre      = item.Nombre
                     
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaLugarNacimientoDTO;
            }
            catch (Exception ex)
            {
                resposeApi.correcto = false;
                resposeApi.Mensaje = ex.Message;
            }
            return Ok(resposeApi);
        }
        [HttpGet]
        [Route("Buscar/{id}")]
        public async Task<IActionResult> Buscar(int id)
        {
            var responseApi = new ResponseApi<LugarNacimientoDTO>();
            var lugarNacimientoDTO = new LugarNacimientoDTO();
            try
            {
                var lugarNacimiento = await _dbContext.LugarNacimientos.FirstOrDefaultAsync(x => x.Id == id);

               if(lugarNacimiento != null) {
                    lugarNacimiento.Id = lugarNacimiento.Id;
                    lugarNacimientoDTO.Nombre = lugarNacimiento.Nombre;
                    
                }
                responseApi.correcto = true;
                responseApi.Valor = lugarNacimientoDTO;
            }
            catch(Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPost]
        [Route("Guardar")]
        public async Task<IActionResult> Guardar(LugarNacimientoDTO lugarNacimiento)
        {
            var responseApi = new ResponseApi<int>();
            
            try
            {
                var DBLugarNacimiento = new LugarNacimiento
                {
                    Nombre = lugarNacimiento.Nombre,
                    Id = lugarNacimiento.Id
                };
                _dbContext.LugarNacimientos.Add(DBLugarNacimiento);
                await _dbContext.SaveChangesAsync();
                if (DBLugarNacimiento.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBLugarNacimiento.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Lugar de nacimiento no registrado";
                }
               
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPut]
        [Route("Editar/{id}")]
        public async Task<IActionResult> Editar(LugarNacimientoDTO lugarNacimiento,int id)
        {
          
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBLugarNacimiento = await _dbContext.LugarNacimientos.FirstOrDefaultAsync(x => x.Id == id);
                
                if (DBLugarNacimiento != null)
                {
                    DBLugarNacimiento.Nombre = lugarNacimiento.Nombre;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBLugarNacimiento.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Lugar de nacimiento no encontrado";
                }

            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpDelete]
        [Route("Delete/{id}")]
        public async Task<IActionResult> Delete( int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBLugarNacimiento = await _dbContext.LugarNacimientos.FirstOrDefaultAsync(x => x.Id == id);

                if (DBLugarNacimiento != null)
                {
                    
                    _dbContext.LugarNacimientos.Remove(DBLugarNacimiento);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBLugarNacimiento.Id;
                    responseApi.Mensaje = "Lugar de nacimiento eliminado Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Lugar de nacimiento no encontrado";
                }

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
