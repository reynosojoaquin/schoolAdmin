using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;
using System;

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
                foreach (var item in await _dbContext.Estudiantes.ToListAsync())
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
                var estudiante = await _dbContext.Estudiantes.FirstOrDefaultAsync(x => x.Id == id);

                if (estudiante != null) {
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
                }
                responseApi.correcto = true;
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

                };
                _dbContext.Estudiantes.Add(DBestudiante);
                await _dbContext.SaveChangesAsync();
                if (DBestudiante.Id != 0)
                {
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
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPut]
        [Route("Editar/{id}")]
        public async Task<IActionResult> Editar(EstudiantesDTO estudiante, int id)
        {

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

                    await _dbContext.SaveChangesAsync();
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

    }
}
