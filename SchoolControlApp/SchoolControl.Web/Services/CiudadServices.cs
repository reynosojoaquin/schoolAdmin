using SchoolControl.Shared;
using System.Net.Http.Json;
namespace SchoolControl.Web.Services
{
    public class CiudadServices : ICiudadServices
    {
        private readonly HttpClient _httpClient;
        public CiudadServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public Task<CiudadDTO> Buscar(int id)
        {
            throw new NotImplementedException();
        }

        public Task<int> Editar(CiudadDTO ciudad)
        {
            throw new NotImplementedException();
        }

        public Task<bool> Eliminar(int id)
        {
            throw new NotImplementedException();
        }

        public Task<int> Guardar(CiudadDTO ciudad)
        {
            throw new NotImplementedException();
        }

        public async Task<List<CiudadDTO>> Lista()
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<CiudadDTO>>>("api/Ciudad/Lista");
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
