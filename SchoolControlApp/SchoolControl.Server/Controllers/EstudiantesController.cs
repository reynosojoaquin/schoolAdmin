using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;
using System;
using OfficeOpenXml;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class EstudianteController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public EstudianteController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<EstudiantesDTO>>();
            var ListaEstudiantesDTO = new List<EstudiantesDTO>();
            try
            {
                foreach (var item in await _dbContext.Estudiantes.Include(h => h.HistoriaClinicas).Include(p => p.Padres).ToListAsync())
                {
                    ListaEstudiantesDTO.Add(new EstudiantesDTO
                    {
                        Id = item.Id,
                        Activo = item.Activo,
                        Apellidos = item.Apellidos,
                        Cedula = item.Cedula,
                        Correo = item.Correo,
                        EstadoCivil = item.EstadoCivil,
                        FechaNacimiento = item.FechaNacimiento,
                        Licencia = item.Licencia,
                        LugarNacimientoId = item.LugarNacimientoId,
                        NacionalidadId = item.NacionalidadId,
                        Nombres = item.Nombres,
                        Sexo = item.Sexo,
                        Url = item.Url,
                        SigerdId = item.SigerdId,
                        cursoID = item.Cursoid.GetValueOrDefault(),
                        promovido = item.Promovido.GetValueOrDefault(),
                        HistoriasClinicas = item.HistoriaClinicas.Select(h => new HistoriaClinicaDTO
                        {
                            Id = h.Id,
                            EstudianteId = h.EstudianteId,
                            Descripcion = h.Descripcion,
                            Tipo = h.Tipo
                        }
                        ).ToList(),
                        Padres = item.Padres.Select(p => new PadresDTO
                        {
                            Id = p.Id,
                            Nombre = p.Nombre,
                            Apellido = p.Apellido,
                            Telefono = p.Telefono,
                            Parentesco = p.Parentesco,
                            EstudianteId = p.EstudianteId
                        }
                        ).ToList(),

                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaEstudiantesDTO;
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
            var responseApi = new ResponseApi<EstudiantesDTO>();
            var estudianteDTO = new EstudiantesDTO();
            try
            {
                var estudiante = await _dbContext.Estudiantes
                    .Include(h => h.HistoriaClinicas)
                    .Include(p => p.Padres)
                    .Include(ln => ln.LugarNacimiento)
                    .Include(n => n.Nacionalidad)
                    .FirstOrDefaultAsync(x => x.Id == id);

                if (estudiante != null)
                {
                    estudianteDTO.Id = estudiante.Id;
                    estudianteDTO.Activo = estudiante.Activo;
                    estudianteDTO.Apellidos = estudiante.Apellidos;
                    estudianteDTO.Cedula = estudiante.Cedula;
                    estudianteDTO.Correo = estudiante.Correo;
                    estudianteDTO.EstadoCivil = estudiante.EstadoCivil;
                    estudianteDTO.FechaNacimiento = estudiante.FechaNacimiento;
                    estudianteDTO.Licencia = estudiante.Licencia;
                    estudianteDTO.LugarNacimientoId = estudiante.LugarNacimientoId;
                    estudianteDTO.NacionalidadId = estudiante.NacionalidadId;
                    estudianteDTO.Nombres = estudiante.Nombres;
                    estudianteDTO.Sexo = estudiante.Sexo;
                    estudianteDTO.Url = estudiante.Url;
                    estudianteDTO.SigerdId = estudiante.SigerdId;
                    estudianteDTO.NumOrden = estudiante.NumOrden;
                    estudianteDTO.cursoID = estudiante.Cursoid.GetValueOrDefault();
                    estudianteDTO.promovido = estudiante.Promovido.GetValueOrDefault();
                    estudianteDTO.HistoriasClinicas = estudiante.HistoriaClinicas.Select(h => new HistoriaClinicaDTO
                    {
                        Id = h.Id,
                        EstudianteId = h.EstudianteId,
                        Descripcion = h.Descripcion,
                        Tipo = h.Tipo
                    }
                    ).ToList();
                    estudianteDTO.Padres = estudiante.Padres.Select(p => new PadresDTO
                    {
                        Id = p.Id,
                        Nombre = p.Nombre,
                        Apellido = p.Apellido,
                        Telefono = p.Telefono,
                        Parentesco = p.Parentesco,
                        EstudianteId = p.EstudianteId
                    }
                    ).ToList();
                    estudianteDTO.LugarNacimiento = new LugarNacimientoDTO
                    {
                        Id = estudiante.LugarNacimiento.Id,
                        Nombre = estudiante.LugarNacimiento.Nombre

                    };
                    estudianteDTO.Nacionalidad = new NacionalidadDTO
                    {
                        Id = estudiante.Nacionalidad.Id,
                        Nombre = estudiante.Nacionalidad.Nombre
                    };
                    responseApi.correcto = true;
                }
                responseApi.Valor = estudianteDTO;
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPost]
        [Route("Guardar")]
        public async Task<IActionResult> Guardar(EstudiantesDTO estudiante)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBestudiante = new Estudiante
                {
                    Activo = estudiante.Activo,
                    Apellidos = estudiante.Apellidos,
                    Cedula = estudiante.Cedula,
                    Correo = estudiante.Correo,
                    EstadoCivil = estudiante.EstadoCivil,
                    FechaNacimiento = estudiante.FechaNacimiento,
                    Licencia = estudiante.Licencia,
                    LugarNacimientoId = estudiante.LugarNacimientoId,
                    NacionalidadId = estudiante.NacionalidadId,
                    Nombres = estudiante.Nombres,
                    Sexo = estudiante.Sexo,
                    Url = estudiante.Url,
                    SigerdId = estudiante.SigerdId,
                    Cursoid = estudiante.cursoID,
                    NumOrden = estudiante.NumOrden,
                    Promovido = estudiante.promovido,
                 };
                _dbContext.Estudiantes.Add(DBestudiante);
                await _dbContext.SaveChangesAsync();
                if (DBestudiante.Id != 0)
                {
                    if(estudiante.Padres.Count > 0)
                    {
                        foreach (PadresDTO CurrentPadre in estudiante.Padres)
                        {
                            Padre DBpadre = new Padre
                            {
                                Nombre = CurrentPadre.Nombre,
                                Apellido = CurrentPadre.Apellido,
                                EstudianteId = DBestudiante.Id,
                                Parentesco = CurrentPadre.Parentesco,
                                Telefono = CurrentPadre.Telefono
                            };
                            _dbContext.Padres.Add(DBpadre);
                        }
                    }
                    if(estudiante.HistoriasClinicas.Count > 0)
                    {
                        foreach (HistoriaClinicaDTO CurrentHistoria in estudiante.HistoriasClinicas)
                        {
                            HistoriaClinica DBhistoriaClinica = new HistoriaClinica
                            {
                                Descripcion = CurrentHistoria.Descripcion,
                                EstudianteId = DBestudiante.Id,
                                Tipo = CurrentHistoria.Tipo
                            };
                            _dbContext.HistoriaClinicas.Add(DBhistoriaClinica);
                        }
                    }
                    
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBestudiante.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Estudiante no registrado";
                }

            }
            catch (Exception ex)
            {
                if (ex.InnerException != null)
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = ex.InnerException.Message;
                   
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = ex.Message;
                }
               
            }
            return Ok(responseApi);
        }

        [HttpPut]
        [Route("Editar/{id}")]
        public async Task<IActionResult> Editar([FromBody]EstudiantesDTO estudiante, [FromRoute] int id)
        {
            if (!ModelState.IsValid)
            {
                // Devuelve detalles del error al cliente
                return BadRequest(ModelState);
            }
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBEstudiante = await _dbContext.Estudiantes.FirstOrDefaultAsync(x => x.Id == id);

                if (DBEstudiante != null)
                {

                    DBEstudiante.Activo = estudiante.Activo;
                    DBEstudiante.Apellidos = estudiante.Apellidos;
                    DBEstudiante.Cedula = estudiante.Cedula;
                    DBEstudiante.Correo = estudiante.Correo;
                    DBEstudiante.EstadoCivil = estudiante.EstadoCivil;
                    DBEstudiante.FechaNacimiento = estudiante.FechaNacimiento;
                    DBEstudiante.Licencia = estudiante.Licencia;
                    DBEstudiante.LugarNacimientoId = estudiante.LugarNacimientoId;
                    DBEstudiante.NacionalidadId = estudiante.NacionalidadId;
                    DBEstudiante.Nombres = estudiante.Nombres;
                    DBEstudiante.Sexo = estudiante.Sexo;
                    DBEstudiante.Url = estudiante.Url;
                    DBEstudiante.SigerdId = estudiante.SigerdId;
                    DBEstudiante.Cursoid = estudiante.cursoID;
                    DBEstudiante.NumOrden = estudiante.NumOrden;
                    DBEstudiante.Promovido = estudiante.promovido;
                    try {
                        await _dbContext.SaveChangesAsync();
                    }catch(Exception ex)
                    {
                        if (ex.InnerException != null)
                        {

                            responseApi.correcto = false;
                            responseApi.Mensaje = ex.InnerException.Message;

                        }
                        else
                        {
                            responseApi.correcto = false;
                            responseApi.Mensaje = ex.Message;
                        }
                    }

                   
                    if (DBEstudiante.Id != 0)
                    {
                        if (estudiante.Padres.Count > 0)
                        {
                            foreach (PadresDTO CurrentPadre in estudiante.Padres)
                            {
                                    var padres = await _dbContext.Padres.Where(x => x.EstudianteId == DBEstudiante.Id).ToListAsync();
                                    _dbContext.Padres.RemoveRange(padres);
                                Padre DBpadre = new Padre
                                    {
                                        Nombre = CurrentPadre.Nombre,
                                        Apellido = CurrentPadre.Apellido,
                                        EstudianteId = DBEstudiante.Id,
                                        Parentesco = CurrentPadre.Parentesco,
                                        Telefono = CurrentPadre.Telefono
                                };
                                    _dbContext.Padres.Add(DBpadre);
                                
                            }
                        }
                        if (estudiante.HistoriasClinicas.Count > 0)
                        {
                            foreach (HistoriaClinicaDTO CurrentHistoria in estudiante.HistoriasClinicas)
                            {
                                var historiales = await _dbContext.HistoriaClinicas.Where(x => x.EstudianteId == DBEstudiante.Id).ToListAsync();
                                _dbContext.HistoriaClinicas.RemoveRange(historiales);

                                HistoriaClinica DBhistoriaClinica = new HistoriaClinica
                                    {
                                        Descripcion = CurrentHistoria.Descripcion,
                                        EstudianteId = DBEstudiante.Id,
                                        Tipo = CurrentHistoria.Tipo
                                    };
                                    _dbContext.HistoriaClinicas.Add(DBhistoriaClinica);
                                                     
                            }
                        }

                        try {
                            await _dbContext.SaveChangesAsync();
                        }
                        catch(Exception ex)
                        {
                         
                            if (ex.InnerException != null)
                            {
                                
                                responseApi.correcto = false;
                                responseApi.Mensaje = ex.InnerException.Message;

                            }
                            else
                            {
                                responseApi.correcto = false;
                                responseApi.Mensaje = ex.Message;
                            }
                        }
                      
                      
                    }


                    responseApi.correcto = true;
                    responseApi.Valor = DBEstudiante.Id;
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

        [HttpDelete]
        [Route("Delete/{id}")]
        public async Task<IActionResult> Delete(int id)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBEstudiante = await _dbContext.Estudiantes.FirstOrDefaultAsync(x => x.Id == id);

                if (DBEstudiante != null)
                {

                    _dbContext.Estudiantes.Remove(DBEstudiante);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBEstudiante.Id;
                    responseApi.Mensaje = "Estudiante eliminado Correctamente";
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

        [HttpGet]
        [Route("getStudentClassRoom")]
        public async Task<IActionResult> getStudentClassRoom(int curso_id)
        {

            var responseApi = new ResponseApi<List<EstudiantesDTO>>();
            var LstStudent = new List<EstudiantesDTO>();
          
                try
                {
                    foreach (var item in await _dbContext.Estudiantes.Where(e => e.Cursoid == curso_id).ToListAsync())
                    {
                        LstStudent.Add(new EstudiantesDTO
                        {
                            Id = item.Id,
                            Activo = item.Activo,
                            Apellidos = item.Apellidos,
                            Cedula = item.Cedula,
                            Correo = item.Correo,
                            EstadoCivil = item.EstadoCivil,
                            FechaNacimiento = item.FechaNacimiento,
                            Licencia = item.Licencia,
                            LugarNacimientoId = item.LugarNacimientoId,
                            NacionalidadId = item.NacionalidadId,
                            Nombres = item.Nombres,
                            Sexo = item.Sexo,
                            Url = item.Url,
                            SigerdId = item.SigerdId,
                            NumOrden = item.NumOrden,
                            cursoID = item.Cursoid.GetValueOrDefault(),
                            promovido = item.Promovido.GetValueOrDefault()
                        });
                    }

                    responseApi.correcto = true;
                    responseApi.Valor = LstStudent;
                }
                catch (Exception ex)
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = ex.Message;
                }
                return Ok(responseApi);
            }



        [HttpGet]
        [Route("getStudentForInscription")]
        public async Task<IActionResult> getStudentForInscripction([FromQuery]int curso_id)
        {

            var responseApi = new ResponseApi<List<EstudiantesDTO>>();
            var LstStudent = new List<EstudiantesDTO>();
            var estudiantes = new List<EstudiantesDTO>();
            var Curso = await _dbContext.SeccionesCursos.Include( s => s.Curso ).FirstOrDefaultAsync(x => x.Id == curso_id);
            try
            {
               if(Curso !=null)
                {
                    if( Curso.Curso.Orden == 0)
                    {
                        estudiantes = (from e in _dbContext.Estudiantes
                                       where e.Esnuevoingreso == true
                                       select new EstudiantesDTO
                                       {
                                           Id = e.Id,
                                           Activo = e.Activo,
                                           Apellidos = e.Apellidos,
                                           Cedula = e.Cedula,
                                           Correo = e.Correo,
                                           EstadoCivil = e.EstadoCivil,
                                           FechaNacimiento = e.FechaNacimiento,
                                           Licencia = e.Licencia,
                                           LugarNacimientoId = e.LugarNacimientoId,
                                           NacionalidadId = e.NacionalidadId,
                                           Nombres = e.Nombres,
                                           Sexo = e.Sexo,
                                           Url = e.Url,
                                           SigerdId = e.SigerdId,
                                           NumOrden = e.NumOrden,
                                           cursoID = e.Cursoid.GetValueOrDefault(),
                                           promovido = e.Promovido.GetValueOrDefault()
                                       }).ToList();


                        foreach (var item in estudiantes)
                        {
                            LstStudent.Add(new EstudiantesDTO
                            {
                                Id = item.Id,
                                Activo = item.Activo,
                                Apellidos = item.Apellidos,
                                Cedula = item.Cedula,
                                Correo = item.Correo,
                                EstadoCivil = item.EstadoCivil,
                                FechaNacimiento = item.FechaNacimiento,
                                Licencia = item.Licencia,
                                LugarNacimientoId = item.LugarNacimientoId,
                                NacionalidadId = item.NacionalidadId,
                                Nombres = item.Nombres,
                                Sexo = item.Sexo,
                                Url = item.Url,
                                SigerdId = item.SigerdId,
                                NumOrden = item.NumOrden,
                                cursoID = item.cursoID,
                                promovido = item.promovido
                            });
                        }
                    }else{

                        estudiantes = (from e in _dbContext.Estudiantes
                                       join s in _dbContext.SeccionesCursos on e.Cursoid equals s.Id        
                                       join c in _dbContext.Cursos on e.Cursoid equals c.Cursoid
                                       where e.Esnuevoingreso == true || c.Orden == (Curso.Curso.Orden - 1)
                                       select new EstudiantesDTO
                                       {
                                           Id = e.Id,
                                           Activo = e.Activo,
                                           Apellidos = e.Apellidos,
                                           Cedula = e.Cedula,
                                           Correo = e.Correo,
                                           EstadoCivil = e.EstadoCivil,
                                           FechaNacimiento = e.FechaNacimiento,
                                           Licencia = e.Licencia,
                                           LugarNacimientoId = e.LugarNacimientoId,
                                           NacionalidadId = e.NacionalidadId,
                                           Nombres = e.Nombres,
                                           Sexo = e.Sexo,
                                           Url = e.Url,
                                           SigerdId = e.SigerdId,
                                           NumOrden = e.NumOrden,
                                           cursoID = e.Cursoid.GetValueOrDefault(),
                                           promovido = e.Promovido.GetValueOrDefault()
                                       }).ToList();


                        foreach (var item in estudiantes)
                        {
                            LstStudent.Add(new EstudiantesDTO
                            {
                                Id = item.Id,
                                Activo = item.Activo,
                                Apellidos = item.Apellidos,
                                Cedula = item.Cedula,
                                Correo = item.Correo,
                                EstadoCivil = item.EstadoCivil,
                                FechaNacimiento = item.FechaNacimiento,
                                Licencia = item.Licencia,
                                LugarNacimientoId = item.LugarNacimientoId,
                                NacionalidadId = item.NacionalidadId,
                                Nombres = item.Nombres,
                                Sexo = item.Sexo,
                                Url = item.Url,
                                SigerdId = item.SigerdId,
                                NumOrden = item.NumOrden,
                                cursoID = item.cursoID,
                                promovido = item.promovido
                            });
                        }

                    }
                    


                             


                } 
               
                responseApi.correcto = true;
                responseApi.Valor = LstStudent;
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

                var estudiantes = new List<EstudiantesDTO>();
                for (int row = 2; row <= rowCount; row++)
                {
                    try
                    {
                        var value = worksheet.Cells[row, 1].Value?.ToString();
                        if(value != null)
                        {
                                estudiantes.Add(new EstudiantesDTO
                                                        {
                                                            Nombres = worksheet.Cells[row, 1].Value?.ToString(),
                                                            Apellidos = worksheet.Cells[row, 2].Value?.ToString() ,
                                                            Cedula = worksheet.Cells[row, 3].Value?.ToString(),
                                                            Sexo = worksheet.Cells[row, 4].Value?.ToString(),
                                                            FechaNacimiento = worksheet.Cells[row, 5].Value?.ToString(),
                                                            SigerdId = worksheet.Cells[row, 6].Value?.ToString(),
                                                        });
                        }
                        
                    }
                    catch (Exception ex)
                    {
                        responseApi.correcto = false;
                        responseApi.Mensaje = $"Error en la fila {row}: {ex.Message}";
                        return BadRequest(responseApi);
                    }
                }

                foreach (var estudiante in estudiantes)
                {
                    _dbContext.Estudiantes.Add(new Estudiante
                    {
                        Nombres = estudiante.Nombres,
                        Apellidos = estudiante.Apellidos,
                        Cedula = estudiante.Cedula,
                        Sexo = estudiante.Sexo,
                        FechaNacimiento = estudiante.FechaNacimiento,
                        SigerdId = estudiante.SigerdId,
                      
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
                if (ex.InnerException != null)
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = ex.InnerException.Message;

                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = $"Error procesando el archivo: {ex.Message}";
                   
                }
               
               
                return StatusCode(500, responseApi);
            }
        }


    }
}
