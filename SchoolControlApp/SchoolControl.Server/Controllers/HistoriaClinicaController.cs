using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class HistoriaClinicaController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public HistoriaClinicaController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<HistoriaClinicaDTO>>();
            var ListaHistoriaClinicaDTO = new List<HistoriaClinicaDTO>();
            try
            {
                foreach (var item in await _dbContext.HistoriaClinicas.ToListAsync())
                {
                    ListaHistoriaClinicaDTO.Add(new HistoriaClinicaDTO
                    {
                        Id          = item.Id,
                        Descripcion = item.Descripcion,
                        EstudianteId = item.EstudianteId,
                        Tipo = item.Tipo,
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaHistoriaClinicaDTO;
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
            var responseApi = new ResponseApi<HistoriaClinicaDTO>();
            var HistoriaClinicaDTO = new HistoriaClinicaDTO();
            try
            {
                var HistoriaClinica = await _dbContext.HistoriaClinicas.FirstOrDefaultAsync(x => x.Id == id);

               if(HistoriaClinica != null) {
                    HistoriaClinicaDTO.Id = HistoriaClinica.Id;
                    HistoriaClinicaDTO.Descripcion = HistoriaClinica.Descripcion;
                    HistoriaClinicaDTO.EstudianteId = HistoriaClinica.EstudianteId;
                    HistoriaClinicaDTO.Tipo = HistoriaClinica.Tipo;
                }
                responseApi.correcto = true;
                responseApi.Valor = HistoriaClinicaDTO;
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
        public async Task<IActionResult> Guardar(HistoriaClinicaDTO HistoriaClinica)
        {
            var responseApi = new ResponseApi<int>();
            
            try
            {
                var DBHistoriaClinica = new HistoriaClinica
                {
                    Tipo = HistoriaClinica.Tipo,
                    EstudianteId = HistoriaClinica.EstudianteId,
                    Descripcion = HistoriaClinica.Descripcion,
                };
               
                _dbContext.HistoriaClinicas.Add(DBHistoriaClinica);
                await _dbContext.SaveChangesAsync();
                if (DBHistoriaClinica.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBHistoriaClinica.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Historia Clinica no registrada";
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
        public async Task<IActionResult> Editar(HistoriaClinicaDTO HistoriaClinica,int id)
        {
          
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBHistoriaClinica = await _dbContext.HistoriaClinicas.FirstOrDefaultAsync(x => x.Id == id);
                
                if (DBHistoriaClinica != null)
                {
                    DBHistoriaClinica.Tipo = HistoriaClinica.Tipo;
                    DBHistoriaClinica.Descripcion = HistoriaClinica.Descripcion;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBHistoriaClinica.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Historia Clinica no encontrada";
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
                var DBHistoriaClinica = await _dbContext.HistoriaClinicas.FirstOrDefaultAsync(x => x.Id == id);

                if (DBHistoriaClinica != null)
                {
                    
                    _dbContext.HistoriaClinicas.Remove(DBHistoriaClinica);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBHistoriaClinica.Id;
                    responseApi.Mensaje = "Historia Clinica eliminada Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Historia Clinica no encontrada";
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
