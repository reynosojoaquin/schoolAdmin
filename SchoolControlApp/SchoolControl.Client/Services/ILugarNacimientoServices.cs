using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface ILugarNacimientoServices
    {
        Task<List<LugarNacimientoDTO>> Lista(int take);
        Task<LugarNacimientoDTO> Buscar(int id);
        Task<int> Editar(LugarNacimientoDTO lugarNacimiento,int id);
        Task<bool> Eliminar(int id);
    }
    
}
