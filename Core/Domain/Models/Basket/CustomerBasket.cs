using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Domain.Models.Basket
{
    public class CustomerBasket
    {
        public string Id { get; set; } // Created From Client

        public IEnumerable<BasketItem> Items { get; set; }

        public string? ClientSecret { get; set; }
        public string? PaymentIntentId { get; set; }
        public int? DeliveryMethodId { get; set; }
        public decimal? ShippingPrice { get; set; }
        



    }
}
