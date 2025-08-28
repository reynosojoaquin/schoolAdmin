using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;

namespace SchoolControl.Client.Validators
{
    // 1. Validador de Teléfono (Actualizado para formato internacional)
    [AttributeUsage(AttributeTargets.Property)]
    public class TelefonoValidoAttribute: ValidationAttribute
    {
        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value == null) return new ValidationResult("El teléfono es requerido");

            var telefono = value.ToString();
            var regex = new Regex(@"^(\+1|1)?[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}$");

            return regex.IsMatch(telefono)
                ? ValidationResult.Success
                : new ValidationResult("Formato inválido. Ejemplo: (809) 555-1234 o 809-555-1234");
        }
    }
}
