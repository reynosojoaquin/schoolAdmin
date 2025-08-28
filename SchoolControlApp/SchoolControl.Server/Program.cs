using SchoolControl.Server.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using OfficeOpenXml;


var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddDbContext<SchoolControlDbContext>(
options =>
{
    options.UseNpgsql( builder.Configuration.GetConnectionString("CadenaPosgres"));
    });

builder.Services.AddCors(opciones => {
    opciones.AddPolicy("politica", app =>
    {
        app.AllowAnyOrigin()
      .AllowAnyHeader()
      .AllowAnyMethod();
    });
});

var key = Encoding.ASCII.GetBytes(builder.Configuration["Jwt:JWT_KEY"]!);
// Configuración de JWT desde appsettings.json
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
}).AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = builder.Configuration["Jwt:Issuer"],
        ValidAudience = builder.Configuration["Jwt:Audience"],
        IssuerSigningKey = new SymmetricSecurityKey(key)
    };
});


builder.Services.AddAuthorization();
AppContext.SetSwitch("EPPlus.ExcelPackage.UseLegacyLicenseContext", true);
var app = builder.Build();

// USER JWT






// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

//app.UseHttpsRedirection();
app.UseCors("politica");
app.UseAuthorization();
app.UseAuthentication();
app.MapControllers();

app.Run();
