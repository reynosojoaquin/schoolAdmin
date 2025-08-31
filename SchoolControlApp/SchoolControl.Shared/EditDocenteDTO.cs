using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchoolControl.Shared
{
    public class EditDocenteDTO
    {
        public int Id { get; set; }

        public string Nombres { get; set; } = null!;

        public string Apellidos { get; set; } = null!;

        public string Cedula { get; set; } = null!;

        public bool? Activo { get; set; }

        public string? Correo { get; set; }

        public string? Sexo { get; set; }

        public string? Url { get; set; }

        public int? NacionalidadId { get; set; }

        public string? EstadoCivil { get; set; }

        public string? Licencia { get; set; }

        public int? LugarNacimientoId { get; set; }

        public DateOnly? FechaNacimiento { get; set; }

        public int? Userid { get; set; }

        public string? Direccion { get; set; }

        public string? Telefono { get; set; }

        public DateOnly? FechaIngreso { get; set; }

        public override string ToString()
        {
            return $"ID: {Id}, " +
                   $"Nombres: {Nombres}, " +
                   $"Apellido: {Apellidos}, " +
                   $"Cedula: {Cedula}, " +
                   $"Activo: {Activo}, " +
                   $"Correo: {Correo}, " +
                   $"Sexo: {Sexo}, " +
                   $"Url: {Url}, " +
                   $"Nacionalidad: {NacionalidadId}, " +
                   $"Estado Civil: {EstadoCivil}, " +
                   $"Licencia: {Licencia}, " +
                   $"Lugar de Nacimiento: {LugarNacimientoId}, " +
                   $"User ID: {Userid}, " +
                   $"Dirección: {Direccion}, " +
                   $"Teléfono: {Telefono}, " +
                   $"Fecha de Ingreso: {FechaIngreso}, " +
                   $"Fecha de Nacimiento: {FechaNacimiento}";
        }

    }
}
