using SchoolControl.Shared;
using System.IO.Pipelines;
using System.Net.Http.Json;

namespace SchoolControl.Web.Services
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

    public async Task<(IEnumerable<ProvinciaDTO>provincias,int totalCount)> GetProvincias(string? filter = "D", int page = 1, int pageSize = 10)
    {
        var  response = await _httpClient.GetFromJsonAsync<ProvinciaResponse>($"http://localhost:5251/api/Provincia/page?filter={filter}&page={page}&pageSize={pageSize}");
       
         // Verifica si la respuesta es nula
    if (response == null) {
        // Maneja el caso en que la respuesta sea nula o vacía
        return (Enumerable.Empty<ProvinciaDTO>(), 0);
    }

    // Retorna las provincias y el total de registros
    return (response.Provincias, response.TotalCount);
    }

      
      
    }
}
