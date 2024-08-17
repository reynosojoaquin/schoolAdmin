using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IDireccionesServices
    {
        Task<List<DireccionesDTO>> Lista();
    }
}
