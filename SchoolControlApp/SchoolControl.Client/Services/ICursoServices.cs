using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface ICursoServices
    {
        Task<List<CursoDTO>> Lista(int take);
        Task<CursoDTO> Buscar(int id);
        Task<int> Guardar(CursoDTO provincia);
        Task<int> Editar(CursoDTO provincia, int id);
        Task<bool> Eliminar(int id);
        Task<List<CursoDTO>> getCoursesTeachers();
    }
}
