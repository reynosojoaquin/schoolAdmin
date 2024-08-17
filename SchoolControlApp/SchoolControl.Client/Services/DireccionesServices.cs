using SchoolControl.Shared;
using System.Net.Http.Json;
namespace SchoolControl.Client.Services
{
    public class DireccionesServices:IDireccionesServices
    {
        public readonly HttpClient _httpClient;
        public DireccionesServices(HttpClient httpClient) {
             _httpClient = httpClient;
        }
        public async Task<List<DireccionesDTO>> Lista()
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<DireccionesDTO>>>("api/Direcciones/Lista");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
    }
}
