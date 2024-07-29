using SchoolControl.Server.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Options;
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
var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors("politica");
app.UseAuthorization();

app.MapControllers();

app.Run();
