using Microsoft.AspNetCore.Components.Forms;
using Microsoft.AspNetCore.Http;
using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface ICursoServices
    {
        Task<List<CursoDTO>> Lista(int take);
        Task<CursoDTO> Buscar(int id);
        Task<int> Guardar(CursoDTO curso);
        Task<int> Editar(CursoDTO curso, int id);
        Task<bool> Eliminar(int id);
        Task<List<CursoDTO>> getCoursesTeachers();
        Task<bool> RemoverEstudiante(int EstudianteID);
        Task<bool> InscribirEstudiante(int cursoID, int EstudianteID);
        Task<bool> RegistroMasivo(MultipartFormDataContent file);
        Task<bool> RegistrarSeccion(SeccionCursoDTO seccion);
        Task<bool> EliminarSeccion(int id);
        Task<int> GuardarSeccion(SeccionCursoDTO seccion);
        Task<int> EditarSeccion(SeccionCursoDTO seccion, int id);
    }
}
