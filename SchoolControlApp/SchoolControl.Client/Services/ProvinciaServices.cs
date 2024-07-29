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
    }
}
