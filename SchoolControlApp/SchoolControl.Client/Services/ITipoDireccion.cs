using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface ITipoDireccion
    {
        Task<List<TipoDireccionDTO>> Lista(); 
        
    }
}
