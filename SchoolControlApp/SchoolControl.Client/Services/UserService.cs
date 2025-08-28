using SchoolControl.Shared;
using System.Net.Http.Json;

namespace SchoolControl.Client.Services
{
    public class UserService:IUserService
    {
        private readonly HttpClient _httpClient;
        public UserService(HttpClient httpClient)
        {

            _httpClient = httpClient;
        }
        public async Task<List<UserDto>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<UserDto>>>("api/User/Lista");
            if (result!.correcto)
            {
                if (take != 0)
                    return result.Valor.Take(take).ToList();
                else
                    return result.Valor.ToList();
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
        public async Task<int> RegisterUser(UserDto user)
        {
            var result = await _httpClient.PostAsJsonAsync($"api/User/Guardar",user);
            var response = await result.Content.ReadFromJsonAsync<ResponseApi<int>>();
            if (response.correcto)
            {
                return response.Valor;
            }
            else
            {
                throw new Exception(response.Mensaje);
            }
        }

        public async Task<SesionDTO> RegisterUserAsync(LoginDto login)
        {
                var result = await _httpClient.GetFromJsonAsync<ResponseApi<SesionDTO>>($"api/User/Login/{login}");
               
                if (result.correcto && result != null)
                {
                    return result.Valor;
                }
                else
                {
                result.correcto = false;
                return result.Valor;
                }
        }

        public async Task<List<PermisosSistemaDTO>> getSystemPermission()
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<PermisosSistemaDTO>>>("api/User/getSystemPermission");
            if (result!.correcto)
            {
               return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }

        public async Task<List<PermisosSistemaDTO>> GetUserPermmissionAsync(int userID)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<PermisosSistemaDTO>>>($"api/User/GetUserPermissionAsync/{userID}");
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
