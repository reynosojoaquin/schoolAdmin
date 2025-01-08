using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface ISectorServices
    {
        Task<List<SectorDTO>> Lista(int take);
        Task<SectorDTO> Buscar(int id);
        Task<int> Guardar(SectorDTO ciudad);
        Task<int> Editar(SectorDTO ciudad, int id);
        Task<bool> Eliminar(int id);
        Task<List<SectorDTO>> GetSectorFiltered(string nombre);
    }
}
