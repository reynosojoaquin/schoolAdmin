using SchoolControl.Shared;

namespace SchoolControl.Client.Services
{
    public interface IRolesService
    {
        public Task<List<RoleDto>> GetRoles();
        public  Task updateSystemPermmisions(PermisosSistemaDTO permisos);
    }
   
}
