using CurrieTechnologies.Razor.SweetAlert2;
using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using SchoolControl.Client;
using SchoolControl.Client.Services;
var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri("http://localhost:5352") });
builder.Services.AddScoped<IProvinciaServices,ProvinciaServices>();
builder.Services.AddScoped<ICiudadServices, CiudadServices>();
builder.Services.AddScoped<ISectorServices, SectorSevices>();
builder.Services.AddScoped<IDireccionesServices, DireccionesServices>();
builder.Services.AddScoped<ITipoDireccion, TipoDireccionesServices>();
builder.Services.AddSweetAlert2();
await builder.Build().RunAsync();
