using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IUserService
    {
        public Task<List<UserDto>> Lista(int take);
        public Task<List<PermisosSistemaDTO>> getSystemPermission();
        public Task<List<PermisosSistemaDTO>> GetUserPermmissionAsync(int userID);
        public Task<int> RegisterUser(UserDto user);
        public Task<SesionDTO> RegisterUserAsync(LoginDto login);
    }
}
