using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface INacionalidadServices
    {
        Task<List<NacionalidadDTO>> Lista(int take);
        Task<NacionalidadDTO> Buscar(int id);
        Task<int> Guardar(NacionalidadDTO ciudad);
        Task<int> Editar(NacionalidadDTO ciudad,int id);
        Task<bool> Eliminar(int id);
    }
    
}
