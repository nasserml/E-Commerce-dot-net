
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Persistence.Repositories
{
    public class UnitOfWork(StoreDbContext context) 
        : IUnitOfWork
    {
        private readonly Dictionary<string, object> _repositories = [];
        public async Task<int> SaveChangesAsync() => await context.SaveChangesAsync();
        public IGenericRepository<TEntity, TKey> GetRepository<TEntity, TKey>()
            where TEntity : BaseEntity<TKey>
        {
            var typeName = typeof(TEntity).Name;

            if (_repositories.ContainsKey(typeName))
                return (IGenericRepository<TEntity, TKey>)_repositories[typeName];



            var repo = new GenericRepository<TEntity, TKey>(context);
            _repositories[typeName] = repo;
            return repo;
        }

        public IGenericRepository<TEntity, int> GetRepository<TEntity>() where TEntity : BaseEntity<int>
        {
            var typeName = typeof(TEntity).Name;

            if (_repositories.ContainsKey(typeName))
                return (IGenericRepository<TEntity, int>)_repositories[typeName];



            var repo = new GenericRepository<TEntity, int>(context);
            _repositories[typeName] = repo;
            return repo;
        }
    }
}


// unitOfWork.GetRepository<Product, int>(); => GenericRepository(TEntity, int)