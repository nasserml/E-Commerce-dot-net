using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Persistence.Repositories
{
    internal class CashRepository(IConnectionMultiplexer connection)
        : ICashRepository
    {
        private readonly IDatabase _database = connection.GetDatabase();
        public async Task<string?> GetAsync(string cashKey)
        {
            var value = await _database.StringGetAsync(cashKey);
            return value.IsNullOrEmpty ? null : value.ToString();
        }

        public async Task SetAsync(string cashkey, string value, TimeSpan expiration)
       => await _database.StringSetAsync(cashkey, value, expiration);
    }
}
