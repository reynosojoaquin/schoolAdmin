using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class SectorController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public SectorController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }

        [HttpGet]
        [Route("Buscar/{id}")]
        public async Task<IActionResult> Buscar(int id)
        {
            var responseApi = new ResponseApi<SectorDTO>();
            var sectorDTO = new SectorDTO();
            try
            {
                var sector = await _dbContext.Sectores.FirstOrDefaultAsync(x => x.Id == id);

                if (sector != null)
                {
                    sectorDTO.Id = sector.Id;
                    sectorDTO.Nombre = sector.Nombre;
                    sectorDTO.CiudadId = sector.CiudadId;
                }
                responseApi.correcto = true;
                responseApi.Valor = sectorDTO;
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = "Error buscando el sector => " + ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> ListSectores()
        {
            var responseApi = new ResponseApi<List<SectorDTO>>();
            var ListaSectoresDTO = new List<SectorDTO>();
            try
            {
                foreach (var item in await _dbContext.Sectores.ToListAsync())
                {
                    ListaSectoresDTO.Add(
                        new SectorDTO
                        {
                            Id = item.Id,
                            Nombre = item.Nombre,
                            CiudadId = item.CiudadId
                        }
                        );
                }
                responseApi.correcto = true;
                responseApi.Valor = ListaSectoresDTO;
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = "error al consultar los sectores => "+ ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPost]
        [Route("Guardar/{id}")]
        public async Task<IActionResult> Guardar(SectorDTO sector)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBSector = new Sectore
                {
                    Nombre = sector.Nombre,
                    CiudadId = sector.CiudadId
                };
                _dbContext.Sectores.Add(DBSector);
                await _dbContext.SaveChangesAsync();
                if (DBSector.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBSector.Id;
                    responseApi.Mensaje = "Sector registrado correctamente";
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
                responseApi.Mensaje = "error registrando el sector => "+ ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPut]
        [Route("Editar/{id}")]
        public async Task<IActionResult> Editar(SectorDTO sector, int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBSector = await _dbContext.Sectores.FirstOrDefaultAsync(x => x.Id == id);

                if (DBSector != null)
                {
                    DBSector.Nombre = sector.Nombre;
                    _dbContext.Sectores.Add(DBSector);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBSector.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Sector no encontrada";
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
                var DBSector = await _dbContext.Sectores.FirstOrDefaultAsync(x => x.Id == id);

                if (DBSector != null)
                {

                    _dbContext.Sectores.Remove(DBSector);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBSector.Id;
                    responseApi.Mensaje = "Sector eliminado Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Sector no encontrado";
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

