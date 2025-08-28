using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IDocentesServices
    {
        Task<List<DocenteDTO>> GetDocentesAsync();
        Task<DocenteDTO?> GetDocenteByIdAsync(int id);
        Task<bool> CreateDocenteAsync(DocenteDTO docente);
        Task<bool> UpdateDocenteAsync(DocenteDTO docente);
        Task<bool> DeleteDocenteAsync(int id);
        Task<bool> RegistroMasivo(MultipartFormDataContent file);
    }
}
