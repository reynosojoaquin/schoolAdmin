using SchoolControl.Shared;

namespace SchoolControl.Web.Services
{
    public interface IDireccionesServices
    {
        Task<List<DireccionesDTO>> Lista();
    }
}
