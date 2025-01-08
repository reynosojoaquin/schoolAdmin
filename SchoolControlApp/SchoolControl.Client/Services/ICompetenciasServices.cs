using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface ICompetenciasServices
    {

        Task<List<CompetenciasDTO>> Lista(int take);
        Task<CompetenciasDTO> Buscar(int id);
        Task<int> Guardar(CompetenciasDTO provincia);
        Task<int> Editar(CompetenciasDTO provincia, int id);
        Task<bool> Eliminar(int id);
    }
}
