using SchoolControl.Shared;
using System.Net.Http.Json;
namespace SchoolControl.Client.Services
{
    public class HistoriaClinicaServices : IHistoriaClinicaServices
    {
        private readonly HttpClient _httpClient;
        public HistoriaClinicaServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<HistoriaClinicaDTO>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<HistoriaClinicaDTO>>>("api/Ciudad/Lista");
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
        public async Task<HistoriaClinicaDTO>Buscar(int id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<HistoriaClinicaDTO>>($"api/Ciudad/Buscar/{id}");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
       
        public async Task<int> Guardar(HistoriaClinicaDTO historia)
        {
          
            var result = await _httpClient.PostAsJsonAsync($"api/Ciudad/Guardar", historia);
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
        public async Task<int> Editar(HistoriaClinicaDTO historia, int id)
        {
           
            var result = new HttpResponseMessage();
            try
            {
                result = await _httpClient.PutAsJsonAsync($"api/Ciudad/Editar/{id}", historia);

            }
            catch (Exception ex)
            {
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
        public async Task<bool>Eliminar(int id)
        {
            var result = await _httpClient.DeleteAsync($"api/HistoriaClinica/Delete/{id}");
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
