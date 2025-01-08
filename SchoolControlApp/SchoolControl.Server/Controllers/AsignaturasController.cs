using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class AsignaturaController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public AsignaturaController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<asignaturaDTO>>();
            var ListaAsignaturaDTO = new List<asignaturaDTO>();
            try
            {
                foreach (var item in await _dbContext.Asignaturas.ToListAsync())
                {
                    ListaAsignaturaDTO.Add(new asignaturaDTO
                    {
                        id            = item.Id,
                        Nombre        = item.Nombre,
                        CursoID       = item.Cursoid, 
                        responsable   = item.Responsable
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaAsignaturaDTO;
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
            var responseApi = new ResponseApi<asignaturaDTO>();
            var asignaturaDTO = new asignaturaDTO();
            try
            {
                var asignatura = await _dbContext.Asignaturas.FirstOrDefaultAsync(x => x.Id == id);

               if(asignatura != null) {
                    asignaturaDTO.id            = asignatura.Id;
                    asignaturaDTO.Nombre        = asignatura.Nombre;
                    asignaturaDTO.CursoID       = asignatura.Cursoid;
                    asignaturaDTO.responsable = asignatura.Responsable;
                }
                responseApi.correcto = true;
                responseApi.Valor = asignaturaDTO;
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
        public async Task<IActionResult> Guardar(asignaturaDTO asignatura)
        {
            var responseApi = new ResponseApi<int>();
            
            try
            {
                var DBasignatura = new Asignatura
                {
                    Nombre      = asignatura.Nombre,
                    Cursoid     = asignatura.CursoID,
                    Responsable = asignatura.responsable

                };
                _dbContext.Asignaturas.Add(DBasignatura);
                await _dbContext.SaveChangesAsync();
                if (DBasignatura.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBasignatura.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Asignatura no registrada";
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
        public async Task<IActionResult> Editar(asignaturaDTO asignatura,int id)
        {
           
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBAsignatura = await _dbContext.Asignaturas.FirstOrDefaultAsync(x => x.Id == id);
                
                if (DBAsignatura != null)
                {
                    DBAsignatura.Nombre = asignatura.Nombre;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBAsignatura.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Asignatura no encontrada";
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
                var DBAsignatura = await _dbContext.Asignaturas.FirstOrDefaultAsync(x => x.Id == id);

                if (DBAsignatura != null)
                {
                    
                    _dbContext.Asignaturas.Remove(DBAsignatura);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBAsignatura.Id;
                    responseApi.Mensaje = "asignatura eliminada Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Asignatura no encontrada";
                }

            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpGet]
        [Route("getAsignaturaTeachers")]
        public async Task<IActionResult> getAsignaturaTeachers(int curso_id,int responsable )
        {

            var responseApi = new ResponseApi<List<asignaturaDTO>>();
            var asignaturasLst = new List<asignaturaDTO>();
            try
            {

                asignaturasLst = 
                     (
                        from _asignatura in _dbContext.Asignaturas
                        join Curso in _dbContext.Cursos
                        on _asignatura.Cursoid equals Curso.Cursoid where Curso.Cursoid == curso_id && _asignatura.Responsable == responsable
                       // group Curso by new { Curso.Cursoid, Curso.Nombre, Curso.Responsable } into cursoGroup
                        select new asignaturaDTO
                        {
                          id             = _asignatura.Id,
                          Nombre         = _asignatura.Nombre,
                          responsable    = _asignatura.Responsable
                        }
                     ).ToList();


                responseApi.correcto = true;
                responseApi.Valor = asignaturasLst;
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
