using System.ComponentModel.DataAnnotations;

namespace Shared.DataTransferObjects.BasketItem
{
    public record BasketItemDTO
    {
        public int Id { get; init; } 
        public string ProductName { get; init; } = default!;
        public string PictureUrl { get; init; } = default!;
        [Range(1,double.MaxValue)]
        public decimal Price { get; init; }
        [Range(1,short.MaxValue)]
        public int Quantity { get; init; }
    }
}
