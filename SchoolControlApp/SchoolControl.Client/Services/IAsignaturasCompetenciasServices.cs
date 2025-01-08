using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IAsignaturasCompetenciasServices
    {
        Task<List<asignaturaDTO>> Lista(int take);
        Task<asignaturaDTO> Buscar(int id);
        Task<int> Guardar(asignaturaDTO provincia);
        Task<int> Editar(asignaturaDTO provincia, int id);
        Task<bool> Eliminar(int id);
    }
}
