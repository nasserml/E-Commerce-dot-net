using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Persistence.Repositories
{
    public static class SpecificationsEvaluator
    {
        public static IQueryable<T> CreateQuery<T>(IQueryable<T> inputQuery, ISpecifications<T> specifications ) 
            where T : class
       {

            var query = inputQuery;
            if (specifications.Criteria is not null)
                query = query.Where(specifications.Criteria);

            //foreach (var include in specifications.IncludeExpressions)
            //    query.Include(include);

            query = specifications.IncludeExpressions.Aggregate(query,
                (currentQuery, include) => currentQuery.Include(include));

            if (specifications.OrderBy is not null)
                query = query.OrderBy(specifications.OrderBy);
            else if (specifications.OrderByDescending is not null)
                query = query.OrderByDescending(specifications.OrderByDescending);

            if (specifications.IsPaginated)
                query = query.Skip(specifications.Skip).Take(specifications.Take);

            return query;


        }
    }
}


//brandId

// Expression = {[Microsoft.EntityFrameworkCore.Query.EntityQueryRootExpression].Where(product => ((Not(value(Services.Specifications.ProductWithBrandAndTypeSpecifications+<>c__DisplayClass1_0).brandId.HasValue) OrElse (product.BrandId == value(Services.Specifications.Prod...

//Expression = {[Microsoft.EntityFrameworkCore.Query.EntityQueryRootExpression].Where(product => ((Not(value(Services.Specifications.ProductWithBrandAndTypeSpecifications+<>c__DisplayClass1_0).brandId.HasValue) OrElse (product.BrandId == value(Services.Specifications.Prod...

//{[Microsoft.EntityFrameworkCore.Query.EntityQueryRootExpression].Where(product => ((Not(value(Services.Specifications.ProductWithBrandAndTypeSpecifications+<>c__DisplayClass1_0).brandId.HasValue) OrElse (product.BrandId == value(Services.Specifications.ProductWithBrandAndTypeSpecifications+<>c__DisplayClass1_0).brandId.Value)) AndAlso (Not(value(Services.Specifications.ProductWithBrandAndTypeSpecifications+<>c__DisplayClass1_0).typeId.HasValue) OrElse (product.TypeId == value(Services.Specifications.ProductWithBrandAndTypeSpecifications+<>c__DisplayClass1_0).typeId.Value)))).Include(p => p.ProductBrand).Include(p => p.ProductType).OrderBy(p => Convert(p.Price, Object))}