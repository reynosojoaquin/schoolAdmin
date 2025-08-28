using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IPadresServices
    {
        Task<List<PadresDTO>> Lista(int take);
        Task<PadresDTO> Buscar(int id);
        Task<int> Guardar(PadresDTO padre);
        Task<int> Editar(PadresDTO padre,int id);
        Task<bool> Eliminar(int id);
    }
}
