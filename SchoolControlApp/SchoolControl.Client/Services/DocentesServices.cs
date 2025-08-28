using System.Net.Http.Json;
using SchoolControl.Shared;
namespace SchoolControl.Client.Services
{
    public class DocentesService : IDocentesServices
    {
        private readonly HttpClient _httpClient;

        public DocentesService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public async Task<List<DocenteDTO>> GetDocentesAsync()
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<DocenteDTO>>>("api/Docentes/lista");
            if (result!.correcto)
            {
             
                    return result.Valor.ToList();
             
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }

        public async Task<DocenteDTO?> GetDocenteByIdAsync(int id)
        {
           
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<DocenteDTO>>($"api/Docentes/Buscar/{id}"); 
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }

        public async Task<bool> CreateDocenteAsync(DocenteDTO docente)
        {
            var response = await _httpClient.PostAsJsonAsync("api/Docentes", docente);
            return response.IsSuccessStatusCode;
        }

        public async Task<bool> UpdateDocenteAsync(DocenteDTO docente)
        {
            var response = await _httpClient.PutAsJsonAsync($"api/Docentes/{docente.ID}", docente);
            return response.IsSuccessStatusCode;
        }

        public async Task<bool> DeleteDocenteAsync(int id)
        {
            var response = await _httpClient.DeleteAsync($"api/Docentes/{id}");
            return response.IsSuccessStatusCode;
        }
        public async Task<bool> RegistroMasivo(MultipartFormDataContent file)
        {
            var result = await _httpClient.PostAsync($"api/Docentes/RegistroMasivo", file);
            var response = await result.Content.ReadFromJsonAsync<ResponseApi<bool>>();
            if (response!.correcto)
            {
                return response.Valor;
            }
            else
            {
                throw new Exception(response.Mensaje);
            }
        }
    }
}