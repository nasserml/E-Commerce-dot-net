using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Shared.DataTransferObjects.Products
{
    public class ProductQueryParameters
    {
        private const int DefaultPageSize = 5;
        private const int MaxPageSize = 10;
        public int? BrandId { get; set; }
        public int? TypeId { get; set; }
        public ProductSortingOptions Options { get; set; }
        public string? Search { get; set; }
        public int PageIndex { get; set; } = 1;
        private int _pageSize = DefaultPageSize;
        public int PageSize { 
            get => _pageSize; 
            set => _pageSize = value > 0 && value < MaxPageSize ? value : DefaultPageSize; }
    }
}
