using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;
namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class DireccionController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public DireccionController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }

        [HttpGet]
        [Route("Buscar/{id}")]
        public async Task<IActionResult> Buscar(int id)
        {
            var responseApi = new ResponseApi<DireccionesDTO>();
            var direccionDTO = new DireccionesDTO();
            try
            {
                var direccion = await _dbContext.Direcciones.FirstOrDefaultAsync(x => x.Id == id);

                if (direccion != null)
                {
                    direccionDTO.Id          = direccion.Id;
                    direccionDTO.Calle       = direccion.Calle;
                    direccionDTO.CiudadId    = direccion.CiudadId;
                    direccionDTO.Numero      = direccion.Numero;
                    direccionDTO.Apartamento = direccion.Apartamento;
                    direccionDTO.Longitud    = direccion.Longitud;
                    direccionDTO.Latitude    = direccion.Latitude;
                    direccionDTO.PersonaId   = direccion.PersonaId;
                    direccionDTO.TipoId      = direccion.TipoId;
                    direccionDTO.ProvinciaId = direccion.ProvinciaId;
                    direccionDTO.SectorId    = direccion.SectorId;

                }
                responseApi.correcto = true;
                responseApi.Valor = direccionDTO;
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = "Error buscando la direccion => " + ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> ListDirecciones()
        {
            var responseApi = new ResponseApi<List<DireccionesDTO>>();
            var ListaDireccionesDTO = new List<DireccionesDTO>();
            try
            {
                foreach (var item in await _dbContext.Direcciones.ToListAsync())
                {
                    ListaDireccionesDTO.Add(
                        new DireccionesDTO
                        {
                            Id            = item.Id,
                            Calle         = item.Calle,
                            CiudadId      = item.CiudadId,
                            Numero        = item.Numero,
                            Apartamento   = item.Apartamento,
                            Longitud      = item.Longitud,
                            Latitude      = item.Latitude,
                            PersonaId     = item.PersonaId,
                            TipoId        = item.TipoId,
                            ProvinciaId   = item.ProvinciaId,
                            SectorId      = item.SectorId
                        }
                        );
                }
                responseApi.correcto = true;
                responseApi.Valor = ListaDireccionesDTO;
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = "error al consultar las direcciones => " + ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPost]
        [Route("Guardar/{id}")]
        public async Task<IActionResult> Guardar(DireccionesDTO direccion)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBDireccion = new Direccione
                {
                    Calle           = direccion.Calle,
                    CiudadId        = direccion.CiudadId,
                    Numero          = direccion.Numero,
                    Apartamento     = direccion.Apartamento,
                    Longitud        = direccion.Longitud,
                    Latitude        = direccion.Latitude,
                    PersonaId       = direccion.PersonaId,
                    TipoId          = direccion.TipoId,
                    ProvinciaId     = direccion.ProvinciaId,
                    SectorId        = direccion.SectorId
                };
                _dbContext.Direcciones.Add(DBDireccion);
                await _dbContext.SaveChangesAsync();
                if (DBDireccion.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBDireccion.Id;
                    responseApi.Mensaje = "Direccion registrada correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Direccion no registrada";
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
        public async Task<IActionResult> Editar(DireccionesDTO direccion, int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBDireccion = await _dbContext.Direcciones.FirstOrDefaultAsync(x => x.Id == id);

                if (DBDireccion != null)
                {
                    DBDireccion.Calle = direccion.Calle;
                    DBDireccion.CiudadId = direccion.CiudadId;
                    DBDireccion.Numero = direccion.Numero;
                    DBDireccion.Apartamento = direccion.Apartamento;
                    DBDireccion.Longitud = direccion.Longitud;
                    DBDireccion.Latitude = direccion.Latitude;
                    DBDireccion.PersonaId = direccion.PersonaId;
                    DBDireccion.TipoId = direccion.TipoId;
                    DBDireccion.ProvinciaId = direccion.ProvinciaId;
                    DBDireccion.SectorId = direccion.SectorId;
                    _dbContext.Direcciones.Add(DBDireccion);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBDireccion.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Direccion  no encontrada";
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
                var DBDireccion = await _dbContext.Direcciones.FirstOrDefaultAsync(x => x.Id == id);

                if (DBDireccion != null)
                {

                    _dbContext.Direcciones.Remove(DBDireccion);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBDireccion.Id;
                    responseApi.Mensaje = "Direccion eliminada Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Direccion no encontrada";
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

