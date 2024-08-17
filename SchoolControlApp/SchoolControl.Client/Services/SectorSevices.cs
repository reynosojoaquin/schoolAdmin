using Microsoft.VisualBasic;
using SchoolControl.Shared;
using System.Net.Http.Json;
namespace SchoolControl.Client.Services
{
    public class SectorSevices: ISectorServices
    {
        private readonly HttpClient _httpClient;
        public SectorSevices(HttpClient httpClient) { 

            _httpClient = httpClient;
        }
        public async Task<List<SectorDTO>> Lista()
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<SectorDTO>>>("api/Sector/Lista");
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
