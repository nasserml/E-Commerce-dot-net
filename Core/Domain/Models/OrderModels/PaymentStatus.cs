namespace Domain.Models.OrderModels
{
    public enum PaymentStatus: byte
    {
        Pending = 0,
        PaymentReceived = 1,
        PaymentFailed = 2
    }
}
