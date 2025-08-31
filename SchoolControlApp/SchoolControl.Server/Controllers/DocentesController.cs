using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using OfficeOpenXml;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Threading.Tasks;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class DocentesController : Controller
    {
        private readonly SchoolControlDbContext _dbContext;
        public DocentesController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<DocenteDTO>>();
            var ListaDocenteDTO = new List<DocenteDTO>();
            try
            {
                foreach (var item in await _dbContext.Docentes.ToListAsync())
                {
                    ListaDocenteDTO.Add(new DocenteDTO
                    {
                        ID = item.Id,
                        Nombres = item.Nombres,
                        Apellido = item.Apellidos,
                        Cedula = item.Cedula,
                        Activo = item.Activo,
                        Correo = item.Correo,
                        Direccion = item.Direccion,
                        EstadoCivil = item.EstadoCivil,
                        FechaIngreso = item.FechaIngreso.ToString(),
                        FechaNacimiento = item.FechaNacimiento.ToString(),
                        Licencia = item.Licencia,
                        LugarNacimiento = item.LugarNacimientoId,
                        Nacionalidad = item.NacionalidadId,
                        Sexo = item.Sexo,
                        Telefono = item.Telefono,
                        Url = item.Url,
                        Userid = item.Userid
                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaDocenteDTO;
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
            var responseApi = new ResponseApi<DocenteDTO>();
            var DocenteDTO = new DocenteDTO();
            try
            {
                var Docente = await _dbContext.Docentes.Include(n=>n.Nacionalidad).Include(ln=>ln.LugarNacimiento).FirstOrDefaultAsync(x => x.Id == id);

                if (Docente != null)
                {
                    DocenteDTO.ID = Docente.Id;
                    DocenteDTO.Nombres = Docente.Nombres;
                    DocenteDTO.Apellido = Docente.Apellidos;
                    DocenteDTO.Cedula = Docente.Cedula ?? string.Empty;
                    DocenteDTO.Activo = Docente.Activo;
                    DocenteDTO.Correo = Docente.Correo ?? string.Empty;
                    DocenteDTO.Direccion = Docente.Direccion;
                    DocenteDTO.EstadoCivil = Docente.EstadoCivil;
                    DocenteDTO.FechaIngreso = Docente.FechaIngreso.ToString();
                    DocenteDTO.FechaNacimiento = Docente.FechaNacimiento.ToString();
                    DocenteDTO.Licencia = Docente.Licencia;
                    DocenteDTO.LugarNacimiento = Docente.LugarNacimiento.Id;
                    DocenteDTO.Nacionalidad = Docente.Nacionalidad.Id;
                    DocenteDTO.Sexo = Docente.Sexo;
                    DocenteDTO.Telefono = Docente.Telefono;
                    DocenteDTO.Url = Docente.Url;
                    DocenteDTO.Userid = Docente.Userid;
                }
                responseApi.correcto = true;
                responseApi.Valor = DocenteDTO;
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
        public async Task<IActionResult> Guardar(DocenteDTO Docente)
        {
            var responseApi = new ResponseApi<int>();

            try
            {
                var DBDocente = new Docente
                {
                    Id = Docente.ID,
                    Nombres = Docente.Nombres,
                    Apellidos = Docente.Apellido,
                    Cedula = Docente.Cedula,
                    Activo = Docente.Activo,
                    Correo = Docente.Correo,
                    Direccion = Docente.Direccion,
                    EstadoCivil = Docente.EstadoCivil,
                    FechaIngreso = DateOnly.FromDateTime(DateTime.ParseExact(Docente.FechaIngreso, "yyyy-MM-dd", CultureInfo.InvariantCulture)),
                    FechaNacimiento = DateOnly.FromDateTime(DateTime.ParseExact(Docente.FechaNacimiento, "yyyy-MM-dd", CultureInfo.InvariantCulture)),
                    Licencia = Docente.Licencia,
                    LugarNacimientoId = Docente.LugarNacimiento,
                    NacionalidadId = Docente.Nacionalidad,
                    Sexo = Docente.Sexo,
                    Telefono = Docente.Telefono,
                    Url = Docente.Url,
                    Userid = Docente.Userid

                };
                _dbContext.Docentes.Add(DBDocente);
                await _dbContext.SaveChangesAsync();
                if (DBDocente.Id != 0)
                {
                    responseApi.correcto = true;
                    responseApi.Valor = DBDocente.Id;
                    responseApi.Mensaje = "Docente registrado con exito";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Docente no registrado";
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
        public async Task<IActionResult> Editar([FromBody] EditDocenteDTO Docente, [FromRoute] int id)
        {

           
            if (!ModelState.IsValid)
            {
                // Devuelve detalles del error al cliente
                return BadRequest(ModelState);
            }

            var responseApi = new ResponseApi<int>();
            try
            {
                var DBDocente = await _dbContext.Docentes.FirstOrDefaultAsync(x => x.Id == Docente.Id);

                if (DBDocente != null)
                {
                    DBDocente.Nombres = Docente.Nombres;
                    DBDocente.Telefono = Docente.Telefono;
                    DBDocente.Direccion = Docente.Direccion;
                    DBDocente.Licencia = Docente.Licencia;
                    DBDocente.NacionalidadId = Docente.NacionalidadId;
                    DBDocente.FechaNacimiento = Docente.FechaNacimiento;
                    DBDocente.LugarNacimientoId = Docente.LugarNacimientoId;
                    DBDocente.Apellidos = Docente.Apellidos;
                    DBDocente.Cedula = Docente.Cedula;
                    DBDocente.Correo = Docente.Correo;
                    DBDocente.Activo = Docente.Activo;
                    DBDocente.EstadoCivil = Docente.EstadoCivil;
                    DBDocente.FechaIngreso = Docente.FechaIngreso; 
                    DBDocente.FechaNacimiento = Docente.FechaNacimiento;
                    DBDocente.Sexo = Docente.Sexo;
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBDocente.Id;
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Docente no encontrada";
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
                var DBDocente = await _dbContext.Docentes.FirstOrDefaultAsync(x => x.Id == id);

                if (DBDocente != null)
                {

                    _dbContext.Docentes.Remove(DBDocente);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBDocente.Id;
                    responseApi.Mensaje = "Docente eliminado Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Docente no encontrado";
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

                var docentes = new List<DocenteDTO>();
                for (int row = 2; row <= rowCount; row++)
                {
                    try
                    {
                        var value = worksheet.Cells[row, 1].Value?.ToString();
                        if (value != null)
                        {
                            docentes.Add(new DocenteDTO
                            {
                                Nombres     = worksheet.Cells[row, 1].Value?.ToString(),
                                Apellido    = worksheet.Cells[row, 2].Value?.ToString(),
                                Cedula      = worksheet.Cells[row, 3].Value?.ToString(),
                                Activo      = worksheet.Cells[row, 4].Value?.ToString() == "1" ? true : false,
                                Correo      = worksheet.Cells[row, 5].Value?.ToString(),
                                Sexo        = worksheet.Cells[row, 6].Value?.ToString(),
                                Nacionalidad = Convert.ToInt16(worksheet.Cells[row, 7].Value?.ToString()),
                                EstadoCivil = worksheet.Cells[row, 8].Value?.ToString(),
                                LugarNacimiento = Convert.ToInt16(worksheet.Cells[row, 9].Value?.ToString()),
                                FechaNacimiento = worksheet.Cells[row, 10].Value?.ToString(),
                                Telefono        = worksheet.Cells[row, 11].Value?.ToString(),
                                FechaIngreso   =  worksheet.Cells[row, 12].Value?.ToString()
                         
                                
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
                foreach (var docente in docentes)
                {
                    _dbContext.Docentes.Add(new Docente
                    {
                        Nombres = docente.Nombres,
                        Apellidos =docente.Apellido,
                        Cedula = docente.Cedula,
                        Activo = docente.Activo,
                        Correo = docente.Correo,
                        Sexo = docente.Sexo,
                        NacionalidadId = docente.Nacionalidad,
                        EstadoCivil = docente.EstadoCivil,
                        LugarNacimientoId = docente.LugarNacimiento,
                        FechaNacimiento = DateOnly.FromDateTime(DateTime.Parse(docente.FechaNacimiento)),
                        Telefono = docente.Telefono,
                        FechaIngreso = DateOnly.FromDateTime(DateTime.Parse(docente.FechaIngreso))

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
