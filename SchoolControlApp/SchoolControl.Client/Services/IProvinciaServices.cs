using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IProvinciaServices
    {
        Task<List<ProvinciaDTO>> Lista(int take);
        Task<ProvinciaDTO> Buscar(int id);
        Task<int> Guardar(ProvinciaDTO provincia);
        Task<int> Editar(ProvinciaDTO provincia,int id);
        Task<bool> Eliminar(int id);
        Task<List<ProvinciaDTO>> GetCountryFiltered(string nombre);
       
       /// Task<IEnumerable<ProvinciaDTO>> GetProvincias(string? filter = null, int page = 1, int pageSize = 10); 
    }
}
