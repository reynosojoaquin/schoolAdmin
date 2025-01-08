using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class DocenteDTO
    {
        public int ID {  get; set; }
        [Required]
        public string Nombres {  get; set; } = string.Empty;
        [Required]
        public string Apellido { get; set; } = string.Empty;
        [Required]
        public string Cedula { get; set; } = string.Empty;
        [Required]
        public bool? Activo { get; set; }  = false;
        [Required]  
        public string Correo { get; set; } = string.Empty;
        [Required]
        public string Sexo { get; set; } = string.Empty;
        [Required]
        public string Url { get; set; } = string.Empty;
        [Required]
        public int? Nacionalidad { get; set; }
        [Required]
        public string EstadoCivil { get; set; } = string.Empty;
        [Required]
        public string Licencia { get; set; } = string.Empty;
        [Required]
        public int? LugarNacimiento { get; set; }
        
        public int? Userid { get; set; }

        public string? Direccion { get; set; }

        public string? Telefono { get; set; }

        public DateOnly? FechaIngreso { get; set; }
        [Required]
        public DateOnly? FechaNacimiento { get; set;}

        public override string ToString()
        {
            return $"ID: {ID}, " +
                   $"Nombres: {Nombres}, " +
                   $"Apellido: {Apellido}, " +
                   $"Cedula: {Cedula}, " +
                   $"Activo: {Activo}, " +
                   $"Correo: {Correo}, " +
                   $"Sexo: {Sexo}, " +
                   $"Url: {Url}, " +
                   $"Nacionalidad: {Nacionalidad}, " +
                   $"Estado Civil: {EstadoCivil}, " +
                   $"Licencia: {Licencia}, " +
                   $"Lugar de Nacimiento: {LugarNacimiento}, " +
                   $"User ID: {Userid}, " +
                   $"Dirección: {Direccion}, " +
                   $"Teléfono: {Telefono}, " +
                   $"Fecha de Ingreso: {FechaIngreso}, " +
                   $"Fecha de Nacimiento: {FechaNacimiento}";
        }

    }
}
