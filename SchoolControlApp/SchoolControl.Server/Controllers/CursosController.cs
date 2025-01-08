using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;


namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class CursosController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public CursosController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<CursoDTO>>();
            var ListaCursoDTO = new List<CursoDTO>();
            try
            {
                foreach (var item in await _dbContext.Cursos.ToListAsync())
                {
                    ListaCursoDTO.Add(new CursoDTO
                    {
                        Cursoid          = item.Cursoid,
                        Nombre      = item.Nombre,
                        
                       
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaCursoDTO;
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
            var responseApi = new ResponseApi<CursoDTO>();
            var CursoDTO = new CursoDTO();
            try
            {
                var ciudad = await _dbContext.Cursos.FirstOrDefaultAsync(x => x.Cursoid == id);

               if(ciudad != null) {
                    CursoDTO.Cursoid = ciudad.Cursoid;
                    CursoDTO.Nombre = ciudad.Nombre;
                   
                }
                responseApi.correcto = true;
                responseApi.Valor = CursoDTO;
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
        public async Task<IActionResult> Guardar(CursoDTO curso)
        {
            var responseApi = new ResponseApi<int>();
            
            try
            {
                var DBCurso = new Curso
                {
                    Nombre = curso.Nombre,
                    Cursoid = curso.Cursoid
                };
                _dbContext.Cursos.Add(DBCurso);
                await _dbContext.SaveChangesAsync();
                if (DBCurso.Cursoid != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBCurso.Cursoid;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Curso no registrado";
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
        public async Task<IActionResult> Editar(CursoDTO ciudad,int id)
        {
            Console.WriteLine("llego a la api ");
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBCurso = await _dbContext.Cursos.FirstOrDefaultAsync(x => x.Cursoid == id);
                
                if (DBCurso != null)
                {
                    DBCurso.Nombre = ciudad.Nombre;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBCurso.Cursoid;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Curso no encontrada";
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
                var DBCurso = await _dbContext.Cursos.FirstOrDefaultAsync(x => x.Cursoid == id);

                if (DBCurso != null)
                {
                    
                    _dbContext.Cursos.Remove(DBCurso);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBCurso.Cursoid;
                    responseApi.Mensaje = "Curso eliminado Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Curso no encontrado";
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
        [Route("getCoursesTeachers")]
        public async Task<IActionResult> getCoursesTeachers(){

            var responseApi = new ResponseApi<List<CursoDTO>>();
            var cursosLst = new List<CursoDTO>();
            try
            { 

                cursosLst =
                     (
                        from _asignatura in _dbContext.Asignaturas
                        join Curso in _dbContext.Cursos
                        on _asignatura.Cursoid equals Curso.Cursoid
                group Curso by new { Curso.Cursoid, Curso.Nombre, Curso.Responsable } into cursoGroup
                select new CursoDTO
                {
                    Cursoid = cursoGroup.Key.Cursoid,
                    Nombre = cursoGroup.Key.Nombre,
                    Responsable = cursoGroup.Key.Responsable,
                }
                     ).ToList();

         
                    responseApi.correcto= true;
                    responseApi.Valor = cursosLst;
            }
            catch(Exception ex)
            {
                responseApi.correcto= false;
                responseApi.Mensaje= ex.Message;
            }
            return Ok(responseApi);
        }

    }
}
