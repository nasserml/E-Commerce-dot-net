using Shared.DataTransferObjects.BasketItem;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ServicesAbstractions
{
    public interface IPaymentService
    {
        Task<BasketDTO> CreateOrUpdatePaymentIntent(string basketId);
        Task UpdateOrderPaymentStatusAsync(string jsonRequest, string stripeHeader);
    }
}
