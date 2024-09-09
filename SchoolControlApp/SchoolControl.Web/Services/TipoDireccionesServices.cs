using SchoolControl.Shared;
using System.Net.Http.Json;

namespace SchoolControl.Web.Services
{
    public class TipoDireccionesServices:ITipoDireccion
    {
        public readonly HttpClient _httpClient;
        public TipoDireccionesServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<TipoDireccionDTO>> Lista()
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<TipoDireccionDTO>>>("api/TipoDirecciones/Lista");
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
