using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using SchoolControl.Server.Models;
using SchoolControl.Shared;
using Microsoft.EntityFrameworkCore;
using Npgsql;
using Microsoft.EntityFrameworkCore.Metadata.Internal;

namespace SchoolControl.Server.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class CalificacionesController : ControllerBase
    {
        private readonly SchoolControlDbContext _dbContext;
        public CalificacionesController(SchoolControlDbContext dbcontext)
        {
            _dbContext = dbcontext;
        }
        [HttpGet]
        [Route("Lista")]
        public async Task<IActionResult> Lista()
        {
            var resposeApi = new ResponseApi<List<CalificacionesDTO>>();
            var ListaCalificacionesDTO = new List<CalificacionesDTO>();
            try
            {
               
                foreach (var item in await _dbContext.Calificaciones.ToListAsync())
                {
                    ListaCalificacionesDTO.Add(new CalificacionesDTO
                    {
                        Id               = item.Id,
                        Estudianteid     = item.Estudianteid,
                        Asigcompid       = item.AsigCompId,
                        P1               = item.P1,
                        P2               = item.P2,
                        P3               = item.P3,
                        P4               = item.P4,

                    });
                }
                resposeApi.correcto = true;
                resposeApi.Valor = ListaCalificacionesDTO;
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
            var responseApi = new ResponseApi<CalificacionesDTO>();
            var CalificacionesDTO = new CalificacionesDTO();
            try
            {
                var calificaciones = await _dbContext.Calificaciones.FirstOrDefaultAsync(x => x.Id == id);

               if(calificaciones != null) {
                    CalificacionesDTO.Id               = calificaciones.Id;
                    CalificacionesDTO.Estudianteid     = calificaciones.Estudianteid;
                    CalificacionesDTO.Asigcompid       = calificaciones.AsigCompId;
                    CalificacionesDTO.P1               = calificaciones.P1;
                    CalificacionesDTO.P2               = calificaciones.P2;
                    CalificacionesDTO.P3               = calificaciones.P3;
                    CalificacionesDTO.P4               = calificaciones.P4;
                }
                responseApi.correcto = true;
                responseApi.Valor = CalificacionesDTO;
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
        public async Task<IActionResult> Guardar( List<CalificacionesDTO> calificaciones)
        {
            var responseApi = new ResponseApi<int>();
            var DBcalificaciones = new Calificacione();
            try
            {
                foreach(var cal in calificaciones)
                {
                    DBcalificaciones = new Calificacione
                    {
                        Estudianteid = cal.Estudianteid,
                        AsigCompId = cal.Asigcompid,
                        P1 = cal.P1,
                        P2 = cal.P2,
                        P3 = cal.P3,
                        P4 = cal.P4,
                        Final = cal.cal_final,
                        Rp1 = cal.cal_rp1,
                        Rp2 = cal.cal_rp2,
                        Rp3 = cal.cal_rp3,
                        Rp4 = cal.cal_rp4,
                        Pp1   = cal.cal_Pp1,    
                        Pp2   = cal.cal_Pp2,
                        Pp3   = cal.cal_Pp3,    
                        Pp4   = cal.cal_Pp4

                    };
                    _dbContext.Calificaciones.Add(DBcalificaciones);
                    await _dbContext.SaveChangesAsync();
                }
               
               
                responseApi.correcto = true;
                responseApi.Mensaje = "Calificaciones Registras con exito";

               
            }
            catch (Exception ex)
            {
                responseApi.correcto = false;
                responseApi.Mensaje = ex.Message;
            }
            return Ok(responseApi);
        }

        [HttpPut]
        [Route("Editar")]
        public async Task<IActionResult> Editar(List<CalificacionesDTO> calificaciones)
        {
           
            var responseApi = new ResponseApi<int>();
            var DBCalificaciones = new Calificacione();
            try
            {
                foreach (var cal in calificaciones)
                {
                    DBCalificaciones = await _dbContext.Calificaciones.FirstOrDefaultAsync(x => x.Id == cal.Id);
                    if (DBCalificaciones != null)
                    {
                       
                        DBCalificaciones.P1 = cal.P1;
                        DBCalificaciones.P2 = cal.P2;
                        DBCalificaciones.P3 = cal.P3;
                        DBCalificaciones.P4 = cal.P4;
                        DBCalificaciones.Final = cal.cal_final;
                        DBCalificaciones.Rp1 = cal.cal_rp1;
                        DBCalificaciones.Rp2 = cal.cal_rp2;
                        DBCalificaciones.Rp3 = cal.cal_rp3;
                        DBCalificaciones.Rp4 = cal.cal_rp4;
                        DBCalificaciones.Pp1 = cal.cal_Pp1;
                        DBCalificaciones.Pp2 = cal.cal_Pp2;
                        DBCalificaciones.Pp3 = cal.cal_Pp3;
                        DBCalificaciones.Pp4 = cal.cal_Pp4;
                      
                    }
                    await _dbContext.SaveChangesAsync();
                }
                
                responseApi.correcto = true;
                responseApi.Valor = 0;
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
                var DBCalificaciones = await _dbContext.Calificaciones.FirstOrDefaultAsync(x => x.Id == id);

                if (DBCalificaciones != null)
                {
                    
                    _dbContext.Calificaciones.Remove(DBCalificaciones);
                    await _dbContext.SaveChangesAsync();
                    responseApi.correcto = true;
                    responseApi.Valor = DBCalificaciones.Id;
                    responseApi.Mensaje = "Calificaciones eliminada Correctamente";
                }
                else
                {
                    responseApi.correcto = false;
                    responseApi.Mensaje = "Calificaciones no encontrada";
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
        [Route("GetDataCalificaciones")]
        public async Task<IActionResult> GetDataCalificaciones()
        {

            var resposeApi = new ResponseApi<List<InfoCalificacionesDTO>>();
            try
            {

                var calificacionesLst = new List<InfoCalificacionesDTO>();
                calificacionesLst = (from calificaciones in _dbContext.Calificaciones
                                     join asig_competencias in _dbContext.AsignaturasCompetencias on
                                          calificaciones.AsigCompId equals asig_competencias.Id
                                     join tbCompetencias in _dbContext.Competencias on asig_competencias.Competenciaid equals tbCompetencias.Id
                                     join tbasignatura in _dbContext.Asignaturas on asig_competencias.Asignaturaid equals tbasignatura.Id 
                                     join tbcurso in _dbContext.Cursos on tbasignatura.Cursoid equals tbcurso.Cursoid
                                     
                                     select new InfoCalificacionesDTO
                                     {
                                             asig_id            = tbasignatura.Id,
                                             cur_id             = tbcurso.Cursoid,   
                                             cur_descripcion    = tbcurso.Nombre,   
                                             asig_descripcion   = tbasignatura.Nombre, 
                                             comp_id            = tbCompetencias.Id,
                                             comp_descripcion   = tbCompetencias.Descripcion,
                                             cal_id             = calificaciones.Id,
                                             cal_est_id         = calificaciones.Estudianteid,
                                             cal_asi_comp_id    = calificaciones.AsigCompId,
                                             cal_p1             = calificaciones.P1,
                                             cal_p2             = calificaciones.P2,
                                             cal_p3             = calificaciones.P3,
                                             cal_p4             = calificaciones.P4,
                                             cal_final       = calificaciones.Final,
                                             cal_rp1            = calificaciones.Rp1,
                                             cal_rp2            = calificaciones.Rp2,
                                             cal_rp3            = calificaciones.Rp3,
                                             cal_rp4            = calificaciones.Rp4,
                                             cal_Pp1 = calificaciones.Pp1,
                                             cal_Pp2 = calificaciones.Pp2,
                                             cal_Pp3 = calificaciones.Pp3,
                                             cal_Pp4 = calificaciones.Pp4                                           
                                                 
                                     }
                                      ).ToList();
                if (calificacionesLst != null)
                {
                    resposeApi.Valor = calificacionesLst;
                    resposeApi.correcto = true;

                }


            }
            catch (Exception e)
            {
                resposeApi.correcto = false;
                resposeApi.Mensaje = e.Message;
            }
            return Ok(resposeApi);
        }
        
    }
}
