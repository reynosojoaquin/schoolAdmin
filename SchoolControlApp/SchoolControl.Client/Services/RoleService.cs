using SchoolControl.Shared;
using System.Net.Http.Json;

namespace SchoolControl.Client.Services
{
    public class RoleService:IRolesService
    {
        private readonly HttpClient _httpClient;
        public RoleService(HttpClient httpClient)
        {

            _httpClient = httpClient;
        }

        public async Task<List<RoleDto>> GetRoles()
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<RoleDto>>>("api/Roles/lista");
            if (result!.correcto)
            {

                return result.Valor.ToList();

            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }

    }

       
    }
