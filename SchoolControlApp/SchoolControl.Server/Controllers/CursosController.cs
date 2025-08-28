using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;
using OfficeOpenXml;
using Microsoft.AspNetCore.Components.Forms;
using System.Linq.Expressions;
using NuGet.Packaging;


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
                foreach (var item in await _dbContext.SeccionesCursos.Include(c => c.Curso).ToListAsync())
                {
                    ListaCursoDTO.Add(new CursoDTO
                    {
                        Cursoid          = item.Curso.Cursoid,
                        Nombre      = item.Curso.Nombre,
                        seccion     = item.Descripcion,
                        Responsable = item.Responsable,
                        seccionID   = item.Id
                       
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
                        join seccion in _dbContext.SeccionesCursos on Curso.Cursoid equals seccion.Cursoid
                        group Curso by new { Curso.Cursoid, Curso.Nombre, seccion.Responsable,seccion.Descripcion,seccion.Id } into cursoGroup
                select new CursoDTO
                {
                    Cursoid = cursoGroup.Key.Cursoid,
                    Nombre = cursoGroup.Key.Nombre,
                    Responsable = cursoGroup.Key.Responsable,
                    seccion = cursoGroup.Key.Descripcion,
                    seccionID = cursoGroup.Key.Id
     
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
        [HttpPost]
        [Route("RemoverEstudiante")]
        public async Task<IActionResult> RemoverEstudiante(int EstudianteID)
        {
            var responseApi = new ResponseApi<bool>();
            var DBEstudiante = await _dbContext.Estudiantes.FirstOrDefaultAsync(x => x.Id == EstudianteID);
            try
            {
                if(DBEstudiante != null)
                {
                    DBEstudiante.Cursoid = 0;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = true;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Estudiante no encontrado";
                }
 
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPost]
        [Route("InscribirEstudiante")]
        public async Task<IActionResult> InscribirEstudiante([FromQuery] int cursoID,[FromQuery]int EstudianteID)
        {
            var responseApi = new ResponseApi<bool>();
            var DBEstudiante = await _dbContext.Estudiantes.FirstOrDefaultAsync(x => x.Id == EstudianteID);
            try
            {
                if (DBEstudiante != null)
                {
                    DBEstudiante.Cursoid = cursoID;
                    DBEstudiante.Promovido = false;
                    DBEstudiante.Esnuevoingreso = false;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = true;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Estudiante no encontrado";
                }

            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }
        [HttpPost]
        [Route("RegistroMasivo")]
        public async Task<IActionResult> RegistroMasivo(IFormFile file)
        {
            var responseApi = new ResponseApi<bool>();
            EPPlusLicense ePPlusLicense = new EPPlusLicense();
            ePPlusLicense.SetNonCommercialPersonal("RTFD");   
           
            if (file == null || file.Length == 0)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = "Archivo no válido o vacío";
                return BadRequest(responseApi);
            }
            try
            {
                using var stream = file.OpenReadStream();
                using var ms = new MemoryStream();
                await stream.CopyToAsync(ms);
                ms.Position = 0;
                using var package = new ExcelPackage(ms);
                var worksheet = package.Workbook.Worksheets[0];
                var rowCount = worksheet.Dimension.Rows;

                var cursos = new List<SeccionCursoDTO>();
                for (int row = 2; row <= rowCount; row++)
                {
                    try
                    {
                        cursos.Add(new SeccionCursoDTO
                        {
                            Descripcion = worksheet.Cells[row, 1].Value?.ToString(),
                            CursoId = int.Parse(worksheet.Cells[row, 2].Value?.ToString() ?? "0"),
                            responsable = worksheet.Cells[row, 3].Value?.ToString()
                        });
                    }
                    catch (Exception ex)
                    {
                        responseApi.correcto = false;
                        responseApi.Mensaje = $"Error en la fila {row}: {ex.Message}";
                        return BadRequest(responseApi);
                    }
                }

                foreach (var curso in cursos)
                {
                    _dbContext.SeccionesCursos.Add(new SeccionesCurso
                    {
                        Cursoid = curso.CursoId,
                        Descripcion = curso.Descripcion,
                        // puedes mapear responsable si tu modelo lo tiene
                        // Responsable = curso.responsable
                    });
                }

                await _dbContext.SaveChangesAsync();

                responseApi.correcto = true;
                responseApi.Valor = true;
                responseApi.Mensaje = "Registro masivo exitoso";
                return Ok(responseApi);
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Valor = false;
                responseApi.Mensaje = $"Error procesando el archivo: {ex.Message}";
                return StatusCode(500, responseApi);
            }
        }

        [HttpPost]
        [Route("RegistrarSeccion")]
        public async Task<IActionResult> RegitrarSeccion(SeccionCursoDTO seccion)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                SeccionesCurso seccionExist = _dbContext.SeccionesCursos.Where(s => s.Cursoid == seccion.CursoId &&
                s.Descripcion == seccion.Descripcion).FirstOrDefault();
               if (seccionExist == null)
                {
                    var DBSeccion = new SeccionesCurso
                    {
                        Cursoid = seccion.CursoId,
                        Descripcion = seccion.Descripcion,
                        Responsable = 0
                    };
                    _dbContext.SeccionesCursos.Add(DBSeccion);
                    await _dbContext.SaveChangesAsync();
                    if (DBSeccion.Cursoid != 0)
                    {
                        responseApi.correcto = true;
                        responseApi.Valor = Convert.ToInt16(DBSeccion.Cursoid);
                    }
                    else
                    {
                        responseApi.correcto = false;
                        responseApi.Mensaje = "Seccion no registrada";
                        return BadRequest(responseApi);
                    }
                    
                }
                else
                {
                    responseApi.Mensaje = "Esta seccion ya fue Creada verifique";
                    responseApi.correcto = false;
                    return BadRequest(responseApi); 
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
        [Route("DeleteSeccion/{id}")]
        public async Task<IActionResult> DeleteSeccion(int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBSeccion = await _dbContext.SeccionesCursos.FirstOrDefaultAsync(x => x.Id == id);

                if (DBSeccion != null)
                {

                    _dbContext.SeccionesCursos.Remove(DBSeccion);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBSeccion.Id;
                    responseApi.Mensaje = "Seccion  eliminada Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Seccion no encontrada";
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
        [Route("EditarSeccion/{id}")]
        public async Task<IActionResult> EditarSeccion(SeccionCursoDTO seccion, int id)
        {

            var responseApi = new ResponseApi<int>();

            try
            {
                var DBSeccion = await _dbContext.SeccionesCursos.FirstOrDefaultAsync(x => x.Id == id);

                if (DBSeccion != null)
                {
                    DBSeccion.Descripcion = seccion.Descripcion;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBSeccion.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Seccion  no encontrada";
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
