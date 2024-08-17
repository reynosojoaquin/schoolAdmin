using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface ISectorServices
    {
        Task<List<SectorDTO>> Lista();
    }
}
