using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using SchoolControl.Server.Models;
using SchoolControl.Shared;

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
                        FechaIngreso = item.FechaIngreso,
                        FechaNacimiento = item.FechaNacimiento,
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
                var Docente = await _dbContext.Docentes.FirstOrDefaultAsync(x => x.Id == id);

                if (Docente != null)
                {
                    DocenteDTO.ID = Docente.Id;
                    DocenteDTO.Nombres = Docente.Nombres;
                    DocenteDTO.Apellido = Docente.Apellidos;
                    DocenteDTO.Cedula = Docente.Cedula;
                    DocenteDTO.Activo = Docente.Activo;
                    DocenteDTO.Correo = Docente.Correo;
                    DocenteDTO.Direccion = Docente.Direccion;
                    DocenteDTO.EstadoCivil = Docente.EstadoCivil;
                    DocenteDTO.FechaIngreso = Docente.FechaIngreso;
                    DocenteDTO.FechaNacimiento = Docente.FechaNacimiento;
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
                    FechaIngreso = Docente.FechaIngreso,
                    FechaNacimiento = Docente.FechaNacimiento,
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
        public async Task<IActionResult> Editar(DocenteDTO Docente, int id)
        {

            var responseApi = new ResponseApi<int>();

            try
            {
                var DBDocente = await _dbContext.Docentes.FirstOrDefaultAsync(x => x.Id == id);

                if (DBDocente != null)
                {
                    DBDocente.Nombres = Docente.Nombres;
                    DBDocente.Telefono = Docente.Telefono;
                    DBDocente.Direccion = Docente.Direccion;
                    DBDocente.Licencia = Docente.Licencia;
                    DBDocente.NacionalidadId = Docente.Nacionalidad;
                    DBDocente.FechaNacimiento = Docente.FechaNacimiento;
                    DBDocente.LugarNacimientoId = Docente.LugarNacimiento;
                    DBDocente.Apellidos = Docente.Apellido;
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

       

    }
}
