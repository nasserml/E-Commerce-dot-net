namespace Domain.Models
{
    // Parent for all Domain models
    public abstract class BaseEntity<Tkey>
    {
        public Tkey Id { get; set; } // Pk
    }
}
