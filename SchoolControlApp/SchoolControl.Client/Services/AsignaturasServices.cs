using SchoolControl.Shared;
using System.Net.Http.Json;
namespace SchoolControl.Client.Services
{
    public class AsignaturaServices : IAsignaturaServices
    {
        private readonly HttpClient _httpClient;
        public AsignaturaServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<asignaturaDTO>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<asignaturaDTO>>>("api/Asignatura/Lista");
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
        public async Task<asignaturaDTO>       Buscar(int id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<asignaturaDTO>>($"api/Asignatura/Buscar/{id}");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
       
        public async Task<int>             Guardar(asignaturaDTO asignatura)
        {
            var result = await _httpClient.PostAsJsonAsync($"api/Asignatura/Guardar", asignatura);
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
        public async Task<int>             Editar(asignaturaDTO asignatura, int id)
        {
         
            var result = new HttpResponseMessage();
            try
            {
                result = await _httpClient.PutAsJsonAsync($"api/Asignatura/Editar/{id}", asignatura);

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
            var result = await _httpClient.DeleteAsync($"api/Asignatura/Delete/{id}");
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
        public async Task<List<asignaturaDTO>> GetCityFiltered(string nombre)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<asignaturaDTO>>>("api/Asignatura/Lista");
            if (result != null && result.Valor != null)
            {

                return result.Valor.Where(p => p.Nombre.Contains(nombre, StringComparison.OrdinalIgnoreCase)).Take(10).ToList();
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }

        public async Task<List<asignaturaDTO>> getAsignaturaTeachers(int curso_id,int responsable)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<asignaturaDTO>>>($"api/Asignatura/getAsignaturaTeachers?curso_id="+curso_id.ToString()+
                "&responsable="+responsable.ToString());
            if (result!.correcto)
            {
                if (result.Valor != null)
                    return result.Valor.ToList();
                else
                    throw new Exception(result.Mensaje);

            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
    }
}
