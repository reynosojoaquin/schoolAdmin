using SchoolControl.Shared;
using System.Net.Http.Json;
namespace SchoolControl.Client.Services
{
    public class CiudadServices : ICiudadServices
    {
        private readonly HttpClient _httpClient;
        public CiudadServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<CiudadDTO>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<CiudadDTO>>>("api/Ciudad/Lista");
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
        public async Task<CiudadDTO>       Buscar(int id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<CiudadDTO>>($"api/Ciudad/Buscar/{id}");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
       
        public async Task<int> Guardar(CiudadDTO Ciudad)
        {
            Console.WriteLine("LLego aqui => " + Ciudad.Id);
            var result = await _httpClient.PostAsJsonAsync($"api/Ciudad/Guardar", Ciudad);
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
        public async Task<int>             Editar(CiudadDTO Ciudad, int id)
        {
            Console.WriteLine("llego al metodo ");
            var result = new HttpResponseMessage();
            try
            {
                result = await _httpClient.PutAsJsonAsync($"api/Ciudad/Editar/{id}", Ciudad);

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
        public async Task<bool>            Eliminar(int id)
        {
            var result = await _httpClient.DeleteAsync($"api/Ciudad/Delete/{id}");
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
        public async Task<List<CiudadDTO>> GetCityFiltered(string nombre)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<CiudadDTO>>>("api/Ciudad/Lista");
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
