using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IHistoriaClinicaServices
    {
        Task<List<HistoriaClinicaDTO>> Lista(int take);
        Task<HistoriaClinicaDTO> Buscar(int id);
        Task<int> Guardar(HistoriaClinicaDTO historia);
        Task<int> Editar(HistoriaClinicaDTO historia,int id);
        Task<bool> Eliminar(int id);
    }
}
