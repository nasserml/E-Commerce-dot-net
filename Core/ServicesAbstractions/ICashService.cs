using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ServicesAbstractions
{
    public interface ICashService
    {
        Task<string?> GetAsync(string cashKey);
        Task SetAsync(string key, object value, TimeSpan expiration);
    }
}
