//using Microsoft.AspNetCore.Http;
//using Microsoft.AspNetCore.Mvc;

//using System.ComponentModel.DataAnnotations;

//namespace E_Commerce.Web.Controllers
//{
//    [Route("api/[controller]")]
//    [ApiController]
//    public class ProductsController : ControllerBase
//    {
//        [HttpGet("{id:int}")]
//        public ActionResult<Product> Get (int id)
//        {
//            return new Product() { Id = id };
//        }

//        [HttpGet]
//        public ActionResult<Product> GetAll([FromQuery] Product product)
//        {
//            return new Product() { Id =100 };
//        }

//        [HttpPost]
//        public ActionResult<Product> Add(Product product)
//        {
//            return new Product() { Id = 100 };
//        }

//        [HttpPut]
//        public ActionResult<Product> Update(Product product)
//        {
//            return new Product() { Id = 100 };
//        }

//        [HttpDelete]
//        public ActionResult<Product> Delete()
//        {
//            return new Product() { Id = 100 };
//        }
//    }

//    public class Product
//    {
//        [Range(1,3)]
//        public int Id { get; set; }
//        [Required]
//        public string Name { get; set; }
//    }
//}
