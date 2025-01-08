using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface ICiudadServices
    {
        Task<List<CiudadDTO>> Lista(int take);
       
        Task<CiudadDTO> Buscar(int id);
        Task<int> Guardar(CiudadDTO ciudad);
        Task<int> Editar(CiudadDTO ciudad,int id);
        Task<bool> Eliminar(int id);
        Task<List<CiudadDTO>> GetCityFiltered(string nombre);
    }
    
}
