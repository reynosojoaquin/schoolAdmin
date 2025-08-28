using SchoolControl.Shared;
using System.Net.Http.Json;
namespace SchoolControl.Client.Services
{
    public class NacionalidadServices : INacionalidadServices
    {
        private readonly HttpClient _httpClient;
        public NacionalidadServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<NacionalidadDTO>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<NacionalidadDTO>>>("api/Nacionalidad/Lista");
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
        public async Task<NacionalidadDTO>       Buscar(int id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<NacionalidadDTO>>($"api/Nacionalidad/Buscar/{id}");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
       
        public async Task<int> Guardar(NacionalidadDTO nacionalidad)
        {
          
            var result = await _httpClient.PostAsJsonAsync($"api/Nacionalidad/Guardar", nacionalidad);
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
        public async Task<int> Editar(NacionalidadDTO Nacionalidad, int id)
        {
           
            var result = new HttpResponseMessage();
            try
            {
                result = await _httpClient.PutAsJsonAsync($"api/Nacionalidad/Editar/{id}", Nacionalidad);

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
        public async Task<bool> Eliminar(int id)
        {
            var result = await _httpClient.DeleteAsync($"api/Nacionalidad/Delete/{id}");
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
        public async Task<List<NacionalidadDTO>> GetCityFiltered(string nombre)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<NacionalidadDTO>>>("api/Nacionalidad/Lista");
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
