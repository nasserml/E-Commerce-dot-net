using Shared.Authentication;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Shared.Orders
{
    public record OrderRequest(string BasketId, AddressDTO ShipToAddress, int DeliveryMethodId);
    
}
