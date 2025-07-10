

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Presentations.Controllers
{
    public class BasketsController(IServiceManager serviceManager) :
        APIController
    {
        // Get Basket By Id
        [HttpGet]
        public async Task<ActionResult<BasketDTO>> Get(string id)
        {
            var basket = await serviceManager.BasketService.GetAsync(id);
            return Ok(basket);
        }


        // Update Basket => Create Basket, Add Item To Basket, Remove Item From Basket
        [HttpPost]
        public async Task<ActionResult<BasketDTO>> Update(BasketDTO basketDTO)
        {
            var basket = await serviceManager.BasketService.UpdateAsync(basketDTO);
            return Ok(basket);
        }

        // Delete Basket
        [HttpDelete("{id}")]
        public async Task<ActionResult<BasketDTO>> Delete( string id)
        {
            var basket = await serviceManager.BasketService.DeleteAsync(id);
            return NoContent(); // 204
        }
    }
}
