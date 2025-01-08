namespace SchoolControl.Shared

{
    public class ResultResponse
    {
        public string Error { get; set; }=string.Empty;
        public bool Success { get; set; }
        public object? Result { get; set; }
    }
}
