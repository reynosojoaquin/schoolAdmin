using SchoolControl.Shared;

namespace SchoolControl.Web.Services
{
    public interface IProvinciaServices
    {
        Task<List<ProvinciaDTO>> Lista();
        Task<ProvinciaDTO> Buscar(int id);
        Task<int> Guardar(ProvinciaDTO provincia);
        Task<int> Editar(ProvinciaDTO provincia);
        Task<bool> Eliminar(int id);
        Task<(IEnumerable<ProvinciaDTO> provincias,int totalCount)> GetProvincias(string? filter = "D", int page = 1, int pageSize = 10); 
    }
}
