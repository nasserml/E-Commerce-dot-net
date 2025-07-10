using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Domain.Models.OrderModels
{
    public class Order : BaseEntity<Guid>
    {
        public Order(string paymentIntentId)
        {
            PaymentIntentId = paymentIntentId;
        }
        public Order(string buyerEmail, ICollection<OrderItem> items, OrderAddress shiptToaddress, DeliveryMethod deliveryMethod, decimal subTotal, string paymentIntentId)
        {
            BuyerEmail = buyerEmail;
            Items = items;
            ShipToAddress = shiptToaddress;
            DeliveryMethod = deliveryMethod;
            //PaymentIntentId = paymentIntentId;
            SubTotal = subTotal;
            PaymentIntentId = paymentIntentId;
        }

        // id
        public string BuyerEmail { get; set; } = default!;
        public DateTimeOffset OrderDate { get; set; } = DateTimeOffset.Now;
        public ICollection<OrderItem> Items { get; set; } = [];
        public OrderAddress ShipToAddress { get; set; } = default!;
        public DeliveryMethod DeliveryMethod { get; set; } = default!;
        public int DeliveryMethodId { get; set; }
        public PaymentStatus Status { get; set; } = PaymentStatus.Pending;
        public string PaymentIntentId { get; set; } = default!;
        public decimal  SubTotal { get; set; }


    }
}
