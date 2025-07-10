using Domain.Models.Products;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Text;
using System.Threading.Tasks;

namespace Services.Specifications
{
    internal class ProductCountSpecifications(ProductQueryParameters parameters) : BaseSpecifications<Product>(CreateCriteria(parameters))
    {
        private static Expression<Func<Product, bool>> CreateCriteria(ProductQueryParameters parameters)
        {
            return product => (!parameters.BrandId.HasValue || product.BrandId == parameters.BrandId.Value) &&
                        (!parameters.TypeId.HasValue || product.TypeId == parameters.TypeId.Value) &&
                        (string.IsNullOrWhiteSpace(parameters.Search) || product.Name.ToLower().Contains(parameters.Search.ToLower()));
        }
    }
}
