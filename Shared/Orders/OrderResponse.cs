using Shared.Authentication;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Shared.Orders
{
    public record OrderResponse
    {

        // id
        public Guid Id { get; set; }
        public string BuyerEmail { get; set; } = default!;
        public DateTimeOffset OrderDate { get; set; }
        public AddressDTO ShipToAddress { get; set; } = default!;
        public string DeliveryMethod { get; set; } = default!;

        public IEnumerable<OrderItemDTO> Items { get; set; } = [];
        public string Status { get; set; }
        public string PaymentIntentId { get; set; } = string.Empty;
        public decimal SubTotal { get; set; }
        public decimal Total { get; set; }
        public decimal DeliveryCost { get; set; }
    }

   public record OrderItemDTO
    {
        public int ProductId { get; set; }
        public string PictureUrl { get; set; }
        public string ProductName { get; set; }
        public decimal Price { get; set; }
        public int Quantity { get; set; }
    }
}
