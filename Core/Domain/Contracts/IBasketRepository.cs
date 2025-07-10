using Domain.Models.Basket;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Domain.Contracts
{
    public interface IBasketRepository
    {
        Task<CustomerBasket?> GetAsync(string id);
        Task<CustomerBasket?> UpdateAsync(CustomerBasket basket, TimeSpan? timeToLive = null); // tll
        Task<bool> DeleteAsync(string id);
    }
}
