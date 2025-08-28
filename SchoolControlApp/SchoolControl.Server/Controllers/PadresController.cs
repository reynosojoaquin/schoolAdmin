using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class PadresController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public PadresController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<PadresDTO>>();
            var ListaPadreDTO = new List<PadresDTO>();
            try
            {
                foreach (var item in await _dbContext.Padres.ToListAsync())
                {
                    ListaPadreDTO.Add(new PadresDTO
                    {
                        Apellido = item.Apellido,
                        Id = item.Id,
                        Nombre = item.Nombre,
                        Parentesco = item.Parentesco,
                        Telefono = item.Telefono,
                        EstudianteId = item.EstudianteId
                            
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaPadreDTO;
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
            var responseApi = new ResponseApi<PadresDTO>();
            var PadresDTO = new PadresDTO();
            try
            {
                var Padre = await _dbContext.Padres.FirstOrDefaultAsync(x => x.Id == id);

               if(Padre != null) {
                    PadresDTO.Id = Padre.Id;
                    PadresDTO.Nombre = Padre.Nombre;
                    PadresDTO.Telefono = Padre.Telefono;
                    PadresDTO.Parentesco = Padre.Parentesco;
                    PadresDTO.EstudianteId = Padre.EstudianteId;
                    PadresDTO.Apellido = Padre.Apellido;
                }
                responseApi.correcto = true;
                responseApi.Valor = PadresDTO;
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
        public async Task<IActionResult> Guardar(PadresDTO Padre)
        {
            var responseApi = new ResponseApi<int>();
            
            try
            {
                var DBPadre = new Padre
                {
                    Apellido = Padre.Apellido,
                    EstudianteId = Padre.EstudianteId,
                    Nombre = Padre.Nombre,
                    Parentesco = Padre.Parentesco,
                    Telefono = Padre.Telefono
                };
               
                _dbContext.Padres.Add(DBPadre);
                await _dbContext.SaveChangesAsync();
                if (DBPadre.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBPadre.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Padre no registrado";
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
        public async Task<IActionResult> Editar(CiudadDTO Padre,int id)
        {
          
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBPadre = await _dbContext.Padres.FirstOrDefaultAsync(x => x.Id == id);
                
                if (DBPadre != null)
                {
                    DBPadre.Nombre = Padre.Nombre;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBPadre.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Padre no encontrado";
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
                var DBPadre = await _dbContext.Padres.FirstOrDefaultAsync(x => x.Id == id);

                if (DBPadre != null)
                {
                    
                    _dbContext.Padres.Remove(DBPadre);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBPadre.Id;
                    responseApi.Mensaje = "Padre eliminado Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Padre no encontrado";
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
