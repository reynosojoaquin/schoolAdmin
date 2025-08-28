using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;
namespace SchoolControl.Client.Extensiones
{
    public class CustomValidations
    {
        /*  // 1. Validador de Teléfono (Actualizado para formato internacional)
          [AttributeUsage(AttributeTargets.Property)]
          public class TelefonoValidoAttribute : ValidationAttribute
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

          // 2. Validador de Email (con dominio específico opcional)
          [AttributeUsage(AttributeTargets.Property)]
          public class EmailValidoAttribute : ValidationAttribute
          {
              protected override ValidationResult IsValid(object value, ValidationContext validationContext)
              {
                  if (value == null) return ValidationResult.Success; // Opcional si no es requerido

                  var email = value.ToString();
                  var regex = new Regex(@"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$");

                  return regex.IsMatch(email)
                      ? ValidationResult.Success
                      : new ValidationResult("Formato de email inválido. Ejemplo: usuario@dominio.com");
              }
          }

          // 3. Validador de Tarjeta de Crédito (con formato y Luhn check)
          [AttributeUsage(AttributeTargets.Property)]
          public class TarjetaCreditoValidaAttribute : ValidationAttribute
          {
              protected override ValidationResult IsValid(object value, ValidationContext validationContext)
              {
                  if (value == null) return ValidationResult.Success;

                  var tarjeta = value.ToString().Replace(" ", "").Replace("-", "");
                  var regex = new Regex(@"^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})$");

                  if (!regex.IsMatch(tarjeta)
                      return new ValidationResult("Formato de tarjeta inválido");

                  // Algoritmo de Luhn
                  int sum = 0;
                  bool alternate = false;
                  for (int i = tarjeta.Length - 1; i >= 0; i--)
                  {
                      var digit = int.Parse(tarjeta[i].ToString());
                      if (alternate)
                      {
                          digit *= 2;
                          if (digit > 9) digit -= 9;
                      }
                      sum += digit;
                      alternate = !alternate;
                  }

                  return (sum % 10 == 0)
                      ? ValidationResult.Success
                      : new ValidationResult("Número de tarjeta inválido");
              }
          }

          // 4. Validador de Cédula Dominicana (con algoritmo de verificación)
          [AttributeUsage(AttributeTargets.Property)]
          public class CedulaDominicanaValidaAttribute : ValidationAttribute
          {
              protected override ValidationResult IsValid(object value, ValidationContext validationContext)
              {
                  if (value == null) return new ValidationResult("La cédula es requerida");

                  var cedula = value.ToString().Replace("-", "");
                  var regex = new Regex(@"^[0-9]{3}-?[0-9]{7}-?[0-9]{1}$");

                  if (!regex.IsMatch(cedula))
                      return new ValidationResult("Formato inválido. Ejemplo: 001-1234567-1");

                  // Algoritmo de validación
                  int verificador = int.Parse(cedula[10].ToString());
                  int total = 0;
                  int[] pesos = { 1, 2, 1, 2, 1, 2, 1, 2, 1, 2 };

                  for (int i = 0; i < 10; i++)
                  {
                      int valor = int.Parse(cedula[i].ToString()) * pesos[i];
                      total += valor > 9 ? valor - 9 : valor;
                  }

                  int digitoVerificador = (10 - (total % 10)) % 10;

                  return (digitoVerificador == verificador)
                      ? ValidationResult.Success
                      : new ValidationResult("Cédula dominicana inválida");
              }
          }
      }*/

    }
}
