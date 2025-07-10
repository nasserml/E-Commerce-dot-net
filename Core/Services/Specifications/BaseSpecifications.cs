using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Text;
using System.Threading.Tasks;

namespace Services.Specifications
{
    internal abstract class BaseSpecifications<T> : ISpecifications<T> where T : class
    {
        protected BaseSpecifications(Expression<Func<T, bool>>? criteria)
        {
            Criteria = criteria;
        }
        public Expression<Func<T, bool>> Criteria { get; private set; }

        public List<Expression<Func<T, object>>> IncludeExpressions { get; } = [];

        public Expression<Func<T, object>> OrderBy { get; private set; }

        public Expression<Func<T, object>> OrderByDescending { get; private set; }

        public int Skip { get; private set; }

        public int Take { get; private set; }

        public bool IsPaginated { get; private set; }

        protected void ApplyPagination(int pageSize, int pageIndex)
        {
            IsPaginated = true;
            Take = pageSize;
            Skip = (pageIndex - 1) * pageSize;
        }

        protected void AddInclude(Expression<Func<T, object>> include) 
            => IncludeExpressions.Add(include);

        protected void AddOrderBy(Expression<Func<T, object>> orderBy) =>
            OrderBy = orderBy;
           
        protected void AddOrderByDescending(Expression<Func<T, object>> orderByDescending) =>
            OrderBy = orderByDescending;

    }
}
