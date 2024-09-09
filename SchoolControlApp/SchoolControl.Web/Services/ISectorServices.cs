using SchoolControl.Shared;

namespace SchoolControl.Web.Services
{
    public interface ISectorServices
    {
        Task<List<SectorDTO>> Lista();
    }
}
