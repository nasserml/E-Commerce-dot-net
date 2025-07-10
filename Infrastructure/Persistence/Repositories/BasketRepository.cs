



using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Persistence.Repositories
{
    public class BasketRepository(IConnectionMultiplexer connectionMultiplexer):
        IBasketRepository
    {

        private readonly IDatabase _database = connectionMultiplexer.GetDatabase();

        public async Task<bool> DeleteAsync(string id) =>
            await _database.KeyDeleteAsync(id);
        

        public async Task<CustomerBasket?> GetAsync(string id)
        {
            // Get object from the database
            // Deserialization 
            var basket = await _database.StringGetAsync(id);

            if (basket.IsNullOrEmpty)
                return null;

            return JsonSerializer.Deserialize<CustomerBasket>(basket);

        }


        // used for create and update
        public async Task<CustomerBasket?> UpdateAsync(CustomerBasket basket, TimeSpan? timeToLive = null)
        {
            var jsonBasket = JsonSerializer.Serialize(basket);

            var isCreatedOrpdtaed = await _database.StringSetAsync(basket.Id,jsonBasket, timeToLive ?? TimeSpan.FromDays(30));

            return isCreatedOrpdtaed ? await GetAsync(basket.Id) : null;
            
        }
    }
}
