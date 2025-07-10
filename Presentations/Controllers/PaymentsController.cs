using Microsoft.Extensions.Logging;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Presentations.Controllers
{
    public class PaymentsController(IServiceManager service)
        : APIController
    {
        [HttpPost("{basketId}")]
        public async Task<ActionResult<BasketDTO>> CreateOrUpdate(string basketId)
        {
            return Ok(await service.PaymentService.CreateOrUpdatePaymentIntent(basketId));
        }

        [HttpPost("WebHook")]
        public async Task<IActionResult> WebHook()
        {
            var json = await new StreamReader(HttpContext.Request.Body).ReadToEndAsync();
            // logic
            await service.PaymentService.UpdateOrderPaymentStatusAsync(json,
               Request.Headers["Stripe-Signature"]);

            return new EmptyResult();
           
        }
    }
}
