using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Shared.DataTransferObjects.Products
{
    public record ProductResponse
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string PictureUrl { get; set; }
        public decimal Price { get; set; }
        public string ProductBrand { get; set; }
        public string ProductType { get; set; }

    };
    
        
  
}

// record ref type
// Equals Based On Value
// Public int Id {get; init; }