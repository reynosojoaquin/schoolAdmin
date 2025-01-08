using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IUserService
    {
        public  Task<int> RegisterUser(UserDto user);
        public Task<SesionDTO> RegisterUserAsync(LoginDto login);
    }
}
