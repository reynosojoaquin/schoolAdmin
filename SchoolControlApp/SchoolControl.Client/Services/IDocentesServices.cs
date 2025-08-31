using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IDocentesServices
    {
        Task<List<DocenteDTO>> GetDocentesAsync();
        Task<DocenteDTO?> GetDocenteByIdAsync(int id);
        Task<bool> CreateDocenteAsync(DocenteDTO docente);
        Task<int> UpdateDocenteAsync(EditDocenteDTO docente);
        Task<bool> DeleteDocenteAsync(int id);
        Task<bool> RegistroMasivo(MultipartFormDataContent file);
        Task<int>Guardar(DocenteDTO docente);
    }
}
