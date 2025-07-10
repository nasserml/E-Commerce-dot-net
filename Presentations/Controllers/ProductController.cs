using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

using ServicesAbstractions;

using Shared.DataTransferObjects;
using Shared.DataTransferObjects.Products;
using Presentations.Attributes;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;

namespace Presentations.Controllers
{
    
    public class ProductsController(IServiceManager serviceManager) 
        : APIController
    {
        // Get All Products => IEnumerable<ProductResponse>
        // Get Product
        // Get All Brands
        // Get All Types

        [RedisCash]
        [HttpGet]
        public async Task<ActionResult<PaginationResponse<ProductResponse>>> GetAllProducts([FromQuery] ProductQueryParameters queryParameters) // Get BaseUrl/api/Products
        {
          
            var products = await serviceManager.ProductService.GetAllProductsAsync(queryParameters);
            return Ok(products);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<ProductResponse>> GetProduct(int id) // Get BaseUrl/api/Products/{id}
        {
            var product = await serviceManager.ProductService.GetProductAsync(id);
            return Ok(product);
        }

        //[Authorize(Roles = "Admin")]
        [HttpGet("brands")]
        public async Task<ActionResult<IEnumerable<BrandResponse>>> GetBrands() // Get BaseUrl/api/Products/brands
        {
            //var email = User.FindFirstValue(ClaimTypes.Email);
            var brands = await serviceManager.ProductService.GetBrandsAsync();
            return Ok(brands);
        }


        [HttpGet("types")]
        public async Task<ActionResult<IEnumerable<TypeResponse>>> GetTypes() // Get BaseUrl/api/Products/types
        {
            var types = await serviceManager.ProductService.GetTypesAsync();
            return Ok(types);
        }



    }
}
