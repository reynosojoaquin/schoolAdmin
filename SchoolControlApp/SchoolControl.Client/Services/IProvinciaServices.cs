using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IProvinciaServices
    {
        Task<List<ProvinciaDTO>> Lista();
    }
}
