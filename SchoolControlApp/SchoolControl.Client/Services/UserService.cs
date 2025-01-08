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
                var result = await _httpClient.GetFromJsonAsync<ResponseApi<SesionDTO>>($"api/Usuarios/Login/{login}");
               
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
    }

       
    }
