using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Forms;
using Microsoft.AspNetCore.Http;
using SchoolControl.Shared;
using System.IO.Pipelines;
using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace SchoolControl.Client.Services
{
    public class CursosServices:ICursoServices
    {
        private readonly HttpClient _httpClient;
        public CursosServices(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }
        public async Task<List<CursoDTO>> Lista(int take)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<CursoDTO>>>("api/Cursos/Lista");
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
        public async Task<CursoDTO> Buscar(int id)
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<CursoDTO>>($"api/Cursos/Buscar/{id}");
            if (result!.correcto)
            {
                return result.Valor;
            }
            else
            {
                throw new Exception(result.Mensaje);
            }
        }
        public async Task<int> Guardar(CursoDTO provincia)
        {

            var result = await _httpClient.PostAsJsonAsync($"api/Cursos/Guardar",provincia);
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

        public async Task<int> Editar(CursoDTO curso,int id)
        {

            var result = new HttpResponseMessage();
            try
            { 
                 result = await _httpClient.PutAsJsonAsync($"api/Cursos/Editar/{id}", curso);

            }
            catch (Exception ex) {
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

        public async Task<bool> Eliminar(int id)
        {
            var result = await _httpClient.DeleteAsync($"api/Cursos/Delete/{id}");
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
       

       public async Task<List<CursoDTO>> getCoursesTeachers()
        {
            var result = await _httpClient.GetFromJsonAsync<ResponseApi<List<CursoDTO>>>($"api/Cursos/getCoursesTeachers");
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
        public async Task<bool>RemoverEstudiante(int estudianteID)
        {
            var result = await _httpClient.PostAsync($"api/Cursos/RemoverEstudiante?EstudianteID={estudianteID}",null);
            var response = await result.Content.ReadFromJsonAsync<ResponseApi<bool>>();
            if (response!.correcto)
            {
                return response.Valor;
            }
            else
            {
                throw new Exception(response.Mensaje);
            }
        }
        public async Task<bool> InscribirEstudiante(int cursoID, int estudianteID)
        {
            var result = await _httpClient.PostAsync($"api/Cursos/InscribirEstudiante?CursoID=" +
                $"{cursoID}&EstudianteID={estudianteID}",null);
            var response = await result.Content.ReadFromJsonAsync<ResponseApi<bool>>();
            if (response!.correcto)
            {
                return response.Valor;
            }
            else
            {
                throw new Exception(response.Mensaje);
            }
        }
        
        public async Task<bool> RegistroMasivo(MultipartFormDataContent file)
        {
            var result = await _httpClient.PostAsync($"api/Cursos/RegistroMasivo",file);
            var response = await result.Content.ReadFromJsonAsync<ResponseApi<bool>>();
            if (response!.correcto)
            {
                return response.Valor;
            }
            else
            {
                throw new Exception(response.Mensaje);
            }
        }

        public async Task<bool> RegistrarSeccion(SeccionCursoDTO seccion)
        {
            var result = await _httpClient.PostAsJsonAsync($"api/Cursos/RegistroSeccion", seccion);
            var response = await result.Content.ReadFromJsonAsync<ResponseApi<bool>>();
            if (response!.correcto)
            {
                return response.Valor;
            }
            else
            {
                throw new Exception(response.Mensaje);
            }
        }

        public async Task<int> GuardarSeccion(SeccionCursoDTO seccion)
        {

            var result = await _httpClient.PostAsJsonAsync($"api/Cursos/RegistrarSeccion", seccion);
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

        public async Task<int> EditarSeccion(SeccionCursoDTO seccion, int id)
        {

            var result = new HttpResponseMessage();
            try
            {
                result = await _httpClient.PutAsJsonAsync($"api/Cursos/EditarSeccion/{id}", seccion);

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

        public async Task<bool> EliminarSeccion(int id)
        {
            var result = await _httpClient.DeleteAsync($"api/Cursos/DeleteSeccion/{id}");
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




    }
}
