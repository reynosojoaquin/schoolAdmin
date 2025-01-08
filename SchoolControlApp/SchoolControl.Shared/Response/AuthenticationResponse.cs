namespace SchoolControl.Shared;

public class AuthenticationResponse
{
    public string Token { get; set; } = string.Empty;
    public string Error { get; set; } = string.Empty;
    public bool Success { get; set; }
}
