using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;
using System.Runtime.InteropServices;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ProvinciaController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public  ProvinciaController(SchoolControlDbContext dbContext) { 
           _dbContext = dbContext;
        }

        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<ProvinciaDTO>>();
            var ListaProvinciasDTO = new List<ProvinciaDTO>();
            try
            {
               foreach(var item in await _dbContext.Provincias.ToListAsync())
                {
                    ListaProvinciasDTO.Add(new ProvinciaDTO
                    {
                        Id = item.Id,
                        Nombre = item.Nombre
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaProvinciasDTO;
            }
            catch(Exception ex)
            {
                resposeApi.correcto = false;
                resposeApi.Mensaje  = ex.Message;
            }
            return Ok(resposeApi);
        }

        [HttpGet]
        [Route("Buscar/{id}")]
        public async Task<IActionResult> Buscar(int id)
        {
            var responseApi = new ResponseApi<ProvinciaDTO>();
            var provinciaDTO = new ProvinciaDTO();
            try
            {
                var provincia = await _dbContext.Provincias.FirstOrDefaultAsync(x => x.Id == id);

                if (provincia != null)
                {
                    provinciaDTO.Id = provincia.Id;
                    provinciaDTO.Nombre = provincia.Nombre;
                
                }
                responseApi.correcto = true;
                responseApi.Valor = provinciaDTO;
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
        public async Task<IActionResult> Guardar(ProvinciaDTO provincia)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBprovincia = new Provincia
                {
                    Nombre = provincia.Nombre
                };
                _dbContext.Provincias.Add(DBprovincia);
                await _dbContext.SaveChangesAsync();
                if (DBprovincia.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBprovincia.Id;
                    responseApi.Mensaje = "Provincia  registrada";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Provincia no registrada";
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
        public async Task<IActionResult> Editar(ProvinciaDTO provincia, int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBProvincia = await _dbContext.Provincias.FirstOrDefaultAsync(x => x.Id == id);

                if (DBProvincia != null)
                {
                    DBProvincia.Nombre = provincia.Nombre;
                    _dbContext.Provincias.Add(DBProvincia);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBProvincia.Id;
                    responseApi.Mensaje = "Provincia modificada con exito";
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
                responseApi.Mensaje = "Error al modificar la provincia => "+ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpDelete]
        [Route("Delete/{id}")]
        public async Task<IActionResult> Delete(int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBProvincia = await _dbContext.Provincias.FirstOrDefaultAsync(x => x.Id == id);

                if (DBProvincia != null)
                {

                    _dbContext.Provincias.Remove(DBProvincia);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBProvincia.Id;
                    responseApi.Mensaje = "Provincia eliminada Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Provincia no encontrada";
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
