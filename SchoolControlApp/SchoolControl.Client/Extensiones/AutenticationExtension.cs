using SchoolControl.Shared;
using Blazored.SessionStorage;
using Microsoft.AspNetCore.Components.Authorization;
using System.Security.Claims;

namespace SchoolControl.Client.Extensiones
{
    public class AutenticationExtension : AuthenticationStateProvider
    {
        private readonly ISessionStorageService _sessionStorageService;
        private readonly ClaimsPrincipal SysInformation = new ClaimsPrincipal(new ClaimsIdentity()); // Usuario no autenticado

        public AutenticationExtension(ISessionStorageService sessionStorageService)
        {
            _sessionStorageService = sessionStorageService;
        }

        public async Task ActualizarEstadoAutenticacion(SesionDTO? sesionUsuario)
        {
            ClaimsPrincipal claimsPrincipal;

            if (sesionUsuario != null)
            {
                // Crear Claims del usuario autenticado
                claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
                {
                    new Claim(ClaimTypes.Name, sesionUsuario.userName),
                    new Claim(ClaimTypes.Email, sesionUsuario.Correo),
                    new Claim(ClaimTypes.Role, sesionUsuario.Rol),
                }, "JwtAuth"));

                await _sessionStorageService.GuardarStorage("sesionUsuario", sesionUsuario);
            }
            else
            {
                // Usuario no autenticado
                claimsPrincipal = SysInformation;
                await _sessionStorageService.RemoveItemAsync("sesionUsuario");
            }

            // Notificar el cambio en el estado de autenticación
            NotifyAuthenticationStateChanged(Task.FromResult(new AuthenticationState(claimsPrincipal)));
        }

        public override async Task<AuthenticationState> GetAuthenticationStateAsync()
        {
            // Obtener el usuario de la sesión almacenada
            var sesionUsuario = await _sessionStorageService.ObtenerStorage<SesionDTO>("sesionUsuario");

            if (sesionUsuario == null)
            {
                // Si no hay sesión, retornar un estado no autenticado
                return new AuthenticationState(SysInformation);
            }

            // Crear Claims del usuario autenticado
            var claimsPrincipal = new ClaimsPrincipal(new ClaimsIdentity(new List<Claim>
            {
                new Claim(ClaimTypes.Name, sesionUsuario.userName),
                new Claim(ClaimTypes.Email, sesionUsuario.Correo),
                new Claim(ClaimTypes.Role, sesionUsuario.Rol),
            }, "JwtAuth"));

            return new AuthenticationState(claimsPrincipal);
        }
    }
}