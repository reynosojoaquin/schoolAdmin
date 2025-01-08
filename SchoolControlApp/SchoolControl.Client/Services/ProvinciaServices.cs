using SchoolControl.Shared;
using System.IO.Pipelines;
using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace SchoolControl.Client.Services
{
    public class ProvinciaServices:IProvinciaServices
    {
        private readonly HttpClient _httpClient;
        public ProvinciaServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<ProvinciaDTO>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<ProvinciaDTO>>>("api/Provincia/Lista");
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

        public async Task<int> Editar(ProvinciaDTO provincia,int id)
        {

            var result = new HttpResponseMessage();
            try
            { 
                 result = await _httpClient.PutAsJsonAsync($"api/Provincia/Editar/{id}", provincia);

            }
            catch (Exception ex) {
                Console.WriteLine(ex.InnerException.Message);
            }

            if (result.IsSuccessStatusCode)
            {
                var evaluar = await result.Content.ReadAsStringAsync();
                var response = await result.Content.ReadFromJsonAsync<ResponseApi<int>>();
                if (response != null)
                {
                    return response.Valor;
                }
                else
                {
                    throw new Exception(response?.Mensaje ?? "Error desconocido al procesar la respuesta.");
                }
            }
            else
            {
                throw new HttpRequestException($"Error en la solicitud HTTP: {result.StatusCode}");
            }
        }

        public async Task<bool> Eliminar(int id)
        {
            var result = await _httpClient.DeleteAsync($"api/Provincia/Delete/{id}");
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
        public async Task<List<ProvinciaDTO>> GetCountryFiltered(string nombre)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<ProvinciaDTO>>>("api/Provincia/Lista");
            if (result != null && result.Valor != null)
            {

                return result.Valor.Where(p => p.Nombre.Contains(nombre, StringComparison.OrdinalIgnoreCase)).Take(10).ToList();
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }

      
    }
}
