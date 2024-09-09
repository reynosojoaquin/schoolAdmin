using SchoolControl.Shared;

namespace SchoolControl.Web.Services
{
    public interface ITipoDireccion
    {
        Task<List<TipoDireccionDTO>> Lista(); 
        
    }
}
