using SchoolControl.Shared;
using System.IO.Pipelines;
using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace SchoolControl.Client.Services
{
    public class PadresServices:IPadresServices
    {
        private readonly HttpClient _httpClient;
        public PadresServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<PadresDTO>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<PadresDTO>>>("api/Provincia/Lista");
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
        public async Task<PadresDTO> Buscar(int id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<PadresDTO>>($"api/Provincia/Buscar/{id}");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
        public async Task<int> Guardar(PadresDTO padre)
        {

            var result = await _httpClient.PostAsJsonAsync($"api/Provincia/Guardar",padre);
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

        public async Task<int> Editar(PadresDTO padre,int id)
        {

            var result = new HttpResponseMessage();
            try
            { 
                 result = await _httpClient.PutAsJsonAsync($"api/Provincia/Editar/{id}", padre);

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
            var result = await _httpClient.DeleteAsync($"api/Padres/Delete/{id}");
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
