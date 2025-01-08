using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IAsignaturaServices
    {
        Task<List<asignaturaDTO>> Lista(int take);
        Task<asignaturaDTO> Buscar(int id);
        Task<int> Guardar(asignaturaDTO asignatura);
        Task<int> Editar(asignaturaDTO asignatura, int id);
        Task<bool> Eliminar(int id);
        Task<List<asignaturaDTO>> getAsignaturaTeachers(int curso_id, int responsable);
    }
}
