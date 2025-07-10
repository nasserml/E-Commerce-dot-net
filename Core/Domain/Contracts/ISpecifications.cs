using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Text;
using System.Threading.Tasks;

namespace Domain.Contracts
{
    public interface ISpecifications<T> where T : class
    {
        Expression<Func<T, bool>> Criteria { get; }
        List<Expression<Func<T, object>>> IncludeExpressions { get; }

        Expression<Func<T, object>> OrderBy { get; }
        Expression<Func<T, object>> OrderByDescending { get; }
        int Skip { get; }
        int Take { get; }
        bool IsPaginated { get; }

    }
}

// where => Criteria Expression<Func<T, bool>>
// Include -> List<Expression<Func<T, object>>>
// Select Criteria Expression<Func<T, TResult>>>
