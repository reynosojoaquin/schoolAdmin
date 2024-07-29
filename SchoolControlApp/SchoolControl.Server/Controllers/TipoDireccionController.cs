using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;
namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class TipoDireccionController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public TipoDireccionController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }

        [HttpGet]
        [Route("Buscar/{id}")]
        public async Task<IActionResult> Buscar(int id)
        {
            var responseApi = new ResponseApi<TipoDireccionDTO>();
            var tipoDireccionDTO = new TipoDireccionDTO();
            try
            {
                var tipoDireccion = await _dbContext.TipoDirecciones.FirstOrDefaultAsync(x => x.Id == id);

                if (tipoDireccion != null)
                {
                    tipoDireccionDTO.Id = tipoDireccion.Id;
                    tipoDireccionDTO.Descripcion = tipoDireccion.Descripcion;
                }
                responseApi.correcto = true;
                responseApi.Valor = tipoDireccionDTO;
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = "Error buscando el tipo de direccion => " + ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> List()
        {
            var responseApi = new ResponseApi<List<TipoDireccionDTO>>();
            var ListaTipoDireccionDTO = new List<TipoDireccionDTO>();
            try
            {
                foreach (var item in await _dbContext.TipoDirecciones.ToListAsync())
                {
                    ListaTipoDireccionDTO.Add(
                        new TipoDireccionDTO
                        {
                            Id          = item.Id,
                           Descripcion  = item.Descripcion
  
                        }
                        );
                }
                responseApi.correcto = true;
                responseApi.Valor = ListaTipoDireccionDTO;
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = "error al consultar los tipos de direcciones => " + ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPost]
        [Route("Guardar/{id}")]
        public async Task<IActionResult> Guardar(TipoDireccionDTO tipoDireccion)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBTipoDireccion = new TipoDireccione
                {
                    Descripcion = tipoDireccion.Descripcion
               
                };
                _dbContext.TipoDirecciones.Add(DBTipoDireccion);
                await _dbContext.SaveChangesAsync();
                if (DBTipoDireccion.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBTipoDireccion.Id;
                    responseApi.Mensaje = "Tipo Direcciones registrada correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Tipo Direcciones no registrada";
                }

            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = "error registrando la direccion => " + ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPut]
        [Route("Editar/{id}")]
        public async Task<IActionResult> Editar(TipoDireccionDTO tipoDireccion, int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBTipoDireccion = await _dbContext.TipoDirecciones.FirstOrDefaultAsync(x => x.Id == id);

                if (DBTipoDireccion != null)
                {
                    DBTipoDireccion.Descripcion = tipoDireccion.Descripcion;
                    _dbContext.TipoDirecciones.Add(DBTipoDireccion);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBTipoDireccion.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "tipo Direccion  no encontrada";
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
        public async Task<IActionResult> Delete(int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBTipoDireccion = await _dbContext.TipoDirecciones.FirstOrDefaultAsync(x => x.Id == id);

                if (DBTipoDireccion != null)
                {

                    _dbContext.TipoDirecciones.Remove(DBTipoDireccion);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBTipoDireccion.Id;
                    responseApi.Mensaje = "Tipo Direccion eliminada Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Tipo Direccion no encontrada";
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
