using Microsoft.AspNetCore.Authorization;

using Shared.Orders;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Presentations.Controllers
{
    [Authorize]
    public class OrdersController(IServiceManager service)
        : APIController
    {
        // Create(address, basketId, deliveryMEthodId ) => OrderResponse
        [HttpPost]
        public async Task<ActionResult<OrderResponse>> Create(OrderRequest request)
        {
            return Ok(await service.OrderService.CreateAsync(request, GetEmailFromToken()));

        }
        // GetAll
        [HttpGet]
        public async Task<ActionResult<IEnumerable<OrderResponse>>> GetAll()
        {  
            return Ok(await service.OrderService.GetALlAsync(GetEmailFromToken()));
        }
        // Get
        [HttpGet("{id:guid}")]
        public async Task<ActionResult<OrderResponse>> Get(Guid id)
        {
            return Ok(await service.OrderService.GetAsync(id));
        }

        // GetDeliveryMethods
        [HttpGet("deliveryMethods")]
        [AllowAnonymous]
        public async Task<ActionResult<IEnumerable<DeliveryMethodResponse>>> GetDeliveryMethods()
        {
            return Ok(await service.OrderService.GetDeliveryMethodsAsync());
        }
    }
}
