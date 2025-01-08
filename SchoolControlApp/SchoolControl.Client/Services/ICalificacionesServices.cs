using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface ICalificacionesServices
    {

        Task<List<CalificacionesDTO>> Lista(int take);
        Task<CalificacionesDTO> Buscar(int id);
        Task<int> Guardar(List<CalificacionesDTO>  calificaciones);
        Task<int> Editar(List<CalificacionesDTO> calificiones);
        Task<bool> Eliminar(int id);
        Task<List<InfoCalificacionesDTO>> GetDatafromFuntionCalificaciones();
    }
}
