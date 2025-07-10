using Shared.Orders;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ServicesAbstractions
{
    public interface IOrderService
    {
        // Create()

        Task<OrderResponse> CreateAsync(OrderRequest request, string email);

        Task<OrderResponse> GetAsync(Guid id);
        Task<IEnumerable<OrderResponse>> GetALlAsync(string email);
        Task<IEnumerable<DeliveryMethodResponse>> GetDeliveryMethodsAsync();

    }
}
