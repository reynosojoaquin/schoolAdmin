using SchoolControl.Shared;
using System.Net.Http.Json;
namespace SchoolControl.Client.Services
{
    public class CalificacionesServices : ICalificacionesServices
    {
        private readonly HttpClient _httpClient;
        public CalificacionesServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<CalificacionesDTO>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<CalificacionesDTO>>>("api/Calificaciones/Lista");
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
        public async Task<CalificacionesDTO>       Buscar(int id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<CalificacionesDTO>>($"api/Calificaciones/Buscar/{id}");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
       
        public async Task<int>  Guardar(List<CalificacionesDTO> Calificaciones)
        {
              var result = await _httpClient.PostAsJsonAsync($"api/Calificaciones/Guardar", Calificaciones);
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
        public async Task<int> Editar(List<CalificacionesDTO> Calificaciones)
        {
            var result = new HttpResponseMessage();
            try
            {
                result = await _httpClient.PutAsJsonAsync($"api/Calificaciones/Editar/", Calificaciones);
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
            var result = await _httpClient.DeleteAsync($"api/Calificaciones/Delete/{id}");
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
        public async Task<List<InfoCalificacionesDTO>> GetDatafromFuntionCalificaciones(int curID,int estID, int asigID)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<InfoCalificacionesDTO>>>($"api/Calificaciones/" +
                $"GetDataCalificaciones/?cursoID={curID}&estudianteID={estID}&asigID={asigID}");
            if (result!.correcto)
            {
                return result.Valor.ToList();
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }

    }
}
