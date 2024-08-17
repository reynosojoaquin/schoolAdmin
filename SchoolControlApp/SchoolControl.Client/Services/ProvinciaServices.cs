using SchoolControl.Shared;
using System.Net.Http.Json;

namespace SchoolControl.Client.Services
{
    public class ProvinciaServices:IProvinciaServices
    {
        private readonly HttpClient _httpClient;
        public ProvinciaServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<ProvinciaDTO>> Lista()
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<ProvinciaDTO>>>("api/Provincia/Lista");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
        public async Task<ProvinciaDTO> Buscar(int id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<ProvinciaDTO>>($"api/Provincia/Buscar/{id}");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
        public async Task<int> Guardar(ProvinciaDTO provincia)
        {

            var result = await _httpClient.PostAsJsonAsync($"api/Provincia/Guardar",provincia);
            var response = await result.Content.ReadFromJsonAsync<ResponseApi<int>>();
            if (response!.correcto)
            {
                return response.Valor;
            }
            else
            {
                throw new Exception(response.Mensaje);
            }
        }

        public async Task<int> Editar(ProvinciaDTO provincia)
        {
            var result = await _httpClient.PutAsJsonAsync($"api/Provincia/Editar/{provincia.Id}", provincia);
            var response = await result.Content.ReadFromJsonAsync<ResponseApi<int>>();
            if (response!.correcto)
            {
                return response.Valor;
            }
            else
            {
                throw new Exception(response.Mensaje);
            }
        }

        public async Task<bool> Eliminar(int id)
        {
            var result = await _httpClient.DeleteAsync($"api/Provincia/Eliminar/{id}");
            var response = await result.Content.ReadFromJsonAsync<ResponseApi<int>>();
            if (response!.correcto)
            {
                return response.correcto;
            }
            else
            {
                throw new Exception(response.Mensaje);
            }
        }

      
      
    }
}
