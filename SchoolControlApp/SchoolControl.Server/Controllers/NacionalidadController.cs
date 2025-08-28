using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class NacionalidadController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public NacionalidadController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<NacionalidadDTO>>();
            var ListaNacionalidadesDTO = new List< NacionalidadDTO>();
            try
            {
                foreach (var item in await _dbContext.Nacionalidades.ToListAsync())
                {
                    ListaNacionalidadesDTO.Add(new NacionalidadDTO
                    {
                        Id          = item.Id,
                        Nombre      = item.Nombre,
                       
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaNacionalidadesDTO;
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
            var responseApi = new ResponseApi<NacionalidadDTO>();
            var NacionalidadDTO = new NacionalidadDTO();
            try
            {
                var nacionalidad = await _dbContext.Nacionalidades.FirstOrDefaultAsync(x => x.Id == id);

               if(nacionalidad != null) {
                    NacionalidadDTO.Id = nacionalidad.Id;
                    NacionalidadDTO.Nombre = nacionalidad.Nombre;
               }
                responseApi.correcto = true;
                responseApi.Valor = NacionalidadDTO;
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
        public async Task<IActionResult> Guardar(NacionalidadDTO nacionalidad)
        {
            var responseApi = new ResponseApi<int>();
            
            try
            {
                var DBNacionalidad = new Nacionalidade
                {
                    Nombre = nacionalidad.Nombre
                };      
                
                _dbContext.Nacionalidades.Add(DBNacionalidad);
                await _dbContext.SaveChangesAsync();
                if (DBNacionalidad.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBNacionalidad.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Nacionalidad no registrada";
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
        public async Task<IActionResult> Editar(NacionalidadDTO nacionalidad,int id)
        {
          
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBNacionalidad = await _dbContext.Nacionalidades.FirstOrDefaultAsync(x => x.Id == id);
                
                if (DBNacionalidad != null)
                {
                    DBNacionalidad.Nombre = nacionalidad.Nombre;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBNacionalidad.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Nacionalidad no encontrada";
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
                var DBNacionalidad = await _dbContext.Nacionalidades.FirstOrDefaultAsync(x => x.Id == id);

                if (DBNacionalidad != null)
                {
                    
                    _dbContext.Nacionalidades.Remove(DBNacionalidad);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBNacionalidad.Id;
                    responseApi.Mensaje = "Nacionalidad eliminada Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Nacionalidad no encontrada";
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
