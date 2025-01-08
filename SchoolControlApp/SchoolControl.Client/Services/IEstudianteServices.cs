using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IEstudianteServices
    {
        Task<List<EstudiantesDTO>> Lista(int take);
        Task<EstudiantesDTO> Buscar(int id);
        Task<int> Guardar(EstudiantesDTO estudiante);
        Task<int> Editar(EstudiantesDTO estudiante, int id);
        Task<bool> Eliminar(int id);
        Task<List<EstudiantesDTO>> getStudentClassRoom(int curso_id);
    }
}
