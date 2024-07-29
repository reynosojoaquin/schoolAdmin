using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class CiudadController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public CiudadController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }

        [HttpGet]
        [Route("Buscar/{id}")]
        public async Task<IActionResult> Buscar(int id)
        {
            var responseApi = new ResponseApi<CiudadDTO>();
            var CiudadDTO = new CiudadDTO();
            try
            {
                var ciudad = await _dbContext.Ciudades.FirstOrDefaultAsync(x => x.Id == id);

               if(ciudad != null) {
                    CiudadDTO.Id = ciudad.Id;
                    CiudadDTO.Nombre = ciudad.Nombre;
                    CiudadDTO.ProvinciaId = ciudad.ProvinciaId;
                }
                responseApi.correcto = true;
                responseApi.Valor = CiudadDTO;
            }
            catch(Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> ListCiudades()
        {
            var responseApi = new ResponseApi<List<CiudadDTO>>();
            var ListaCiudadesDTO = new List<CiudadDTO>();
            try
            {
                foreach (var item in await _dbContext.Ciudades.ToListAsync())
                {
                    ListaCiudadesDTO.Add(
                        new CiudadDTO
                        {
                            Id = item.Id,
                            Nombre = item.Nombre,
                            ProvinciaId = item.ProvinciaId

                        }
                        );
                }
                responseApi.correcto = true;
                responseApi.Valor = ListaCiudadesDTO;
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPost]
        [Route("Guardar/{id}")]
        public async Task<IActionResult> Guardar(CiudadDTO ciudad)
        {
            var responseApi = new ResponseApi<int>();
            
            try
            {
                var DBCiudad = new Ciudade
                {
                    Nombre = ciudad.Nombre,
                    ProvinciaId = ciudad.ProvinciaId
                };
                _dbContext.Ciudades.Add(DBCiudad);
                await _dbContext.SaveChangesAsync();
                if (DBCiudad.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBCiudad.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Ciudad no registrada";
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
        public async Task<IActionResult> Editar(CiudadDTO ciudad,int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBCiudad = await _dbContext.Ciudades.FirstOrDefaultAsync(x => x.Id == id);
                
                if (DBCiudad != null)
                {
                    DBCiudad.Nombre = ciudad.Nombre;
                    _dbContext.Ciudades.Add(DBCiudad);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBCiudad.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Ciudad no encontrada";
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
                var DBCiudad = await _dbContext.Ciudades.FirstOrDefaultAsync(x => x.Id == id);

                if (DBCiudad != null)
                {
                    
                    _dbContext.Ciudades.Remove(DBCiudad);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBCiudad.Id;
                    responseApi.Mensaje = "Ciudad eliminada Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Ciudad no encontrada";
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
