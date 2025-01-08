using SchoolControl.Shared;
using System.Net.Http.Json;
namespace SchoolControl.Client.Services
{
    public class EstudiantesServices : IEstudianteServices
    {
        private readonly HttpClient _httpClient;
        public EstudiantesServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<EstudiantesDTO>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<EstudiantesDTO>>>("api/Estudiantes/Lista");
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
        public async Task<EstudiantesDTO>Buscar(int id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<EstudiantesDTO>>($"api/Estudiantes/Buscar/{id}");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
       
        public async Task<int>Guardar(EstudiantesDTO estudiante)
        {
            var result = await _httpClient.PostAsJsonAsync($"api/Estudiantes/Guardar", estudiante);
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
        public async Task<int>Editar(EstudiantesDTO estudiante, int id)
        {
         
            var result = new HttpResponseMessage();
            try
            {
                result = await _httpClient.PutAsJsonAsync($"api/Estudiantes/Editar/{id}", estudiante);

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
        public async Task<bool>Eliminar(int id)
        {
            var result = await _httpClient.DeleteAsync($"api/Estudiantes/Delete/{id}");
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
        public async Task<List<EstudiantesDTO>> GetStudentFiltered(string nombre)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<EstudiantesDTO>>>("api/Estudiantes/Lista");
            if (result != null && result.Valor != null)
            {

                return result.Valor.Where(p => p.Nombres.Contains(nombre, StringComparison.OrdinalIgnoreCase)).Take(10).ToList();
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }

        public async Task<List<EstudiantesDTO>> getStudentClassRoom(int curso_id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<EstudiantesDTO>>>($"api/Estudiante/getStudentClassRoom?curso_id=" +curso_id.ToString());
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
