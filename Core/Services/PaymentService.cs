

global using Product = Domain.Models.Products.Product;

using Microsoft.Extensions.Configuration;

using Stripe;
using Stripe.Forwarding;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Services
{
    internal class PaymentService(IBasketRepository basketRepository, 
        IUnitOfWork unitOfWork,
        IConfiguration configuration,
        IMapper mapper)
        : IPaymentService
    {
        public async Task<BasketDTO> CreateOrUpdatePaymentIntent(string basketId)
        {
            StripeConfiguration.ApiKey = configuration.GetRequiredSection("Stripe")["SecretKey"];

            // BasketRepo => Get Basket
            var basket = await basketRepository.GetAsync(basketId)
                ?? throw new BasketNotFoundException(basketId);

            var productRepo = unitOfWork.GetRepository<Product>();

            foreach(var item in basket.Items)
            {
                var product = await productRepo.GetAsync(item.Id)
                    ?? throw new ProductNotFoundException(item.Id);
                item.Price = product.Price;
            }

            ArgumentNullException.ThrowIfNull(basket.DeliveryMethodId);

            var method = await unitOfWork.GetRepository<DeliveryMethod>()
                .GetAsync(basket.DeliveryMethodId.Value) 
                ?? throw new DeliveryMethodNotFoundException(basket.DeliveryMethodId.Value) ;

            basket.ShippingPrice = method.Cost;

            var amount = (long)(basket.Items.Sum(item => item.Quantity * item.Price) + method.Cost) * 100;

            var service = new PaymentIntentService();

            if(string.IsNullOrWhiteSpace(basket.PaymentIntentId) )
            {
                var options = new PaymentIntentCreateOptions
                {
                    Amount = amount,
                    Currency = "AED",
                    PaymentMethodTypes = ["card"]
                };

                var paymentIntent = await service.CreateAsync(options);

                basket.PaymentIntentId = paymentIntent.Id;
                basket.ClientSecret = paymentIntent.ClientSecret;
            }
            else
            {
                var options = new PaymentIntentUpdateOptions
                {
                    Amount = amount
                };

                await service.UpdateAsync(basket.PaymentIntentId, options);

            }

            await basketRepository.UpdateAsync(basket);
            return mapper.Map<BasketDTO>(basket);

        }

        public async Task UpdateOrderPaymentStatusAsync(string jsonRequest, string stripeHeader)
        {
            var endpointSecret = configuration.GetRequiredSection("Stripe")["EndPointSecret"];
            var stripeEvent = EventUtility.ConstructEvent(jsonRequest,
                   stripeHeader, endpointSecret);

            var paymentIntent = stripeEvent.Data.Object as PaymentIntent;



            // Handle the event
            switch (stripeEvent.Type)
            {
                case EventTypes.PaymentIntentPaymentFailed:
                    await UpdatePaymentFailedAsync(paymentIntent.Id);
                    break;
                case EventTypes.PaymentIntentSucceeded:
                    await UpdatePaymentRecievedAsync(paymentIntent.Id);
                    break;
                // ... handle other event types
                default:
                    Console.WriteLine("Unhandled event type: {0}", stripeEvent.Type);
                    break;
            }


        }

        private async Task UpdatePaymentRecievedAsync(string paymentIntentId)
        {
            var order = await unitOfWork.GetRepository<Order, Guid>()
                .GetAsync(new OrderWithPaymentIntentSpecification(paymentIntentId));

            order.Status = PaymentStatus.PaymentReceived;
            unitOfWork.GetRepository<Order, Guid>().Update(order);

            await unitOfWork.SaveChangesAsync();
        }
        private async Task UpdatePaymentFailedAsync(string paymentIntentId)
        {
            var order = await unitOfWork.GetRepository<Order, Guid>()
                .GetAsync(new OrderWithPaymentIntentSpecification(paymentIntentId));

            order.Status = PaymentStatus.PaymentFailed;
            unitOfWork.GetRepository<Order, Guid>().Update(order);

            await unitOfWork.SaveChangesAsync();
        }
    }
}
