using SchoolControl.Shared;

namespace SchoolControl.Web.Services
{
    public interface ICiudadServices
    {
        Task<List<CiudadDTO>> Lista();
       
        Task<CiudadDTO> Buscar(int id);
        Task<int> Guardar(CiudadDTO ciudad);
        Task<int> Editar(CiudadDTO ciudad);
        Task<bool> Eliminar(int id);
    }
    
}
