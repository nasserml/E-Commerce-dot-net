using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Persistence.Repositories
{
    internal class GenericRepository<TEntity, TKey>(StoreDbContext context)
        : IGenericRepository<TEntity, TKey>
        where TEntity : BaseEntity<TKey>
    {
        public void Add(TEntity entity) => context.Set<TEntity>().Add(entity);

        public void Delete(TEntity entity) => context.Set<TEntity>().Remove(entity);

        public void Update(TEntity entity) => context.Set<TEntity>().Update(entity);



        public async Task<IEnumerable<TEntity>> GetAllAsync(bool trackChanges = false) =>
            trackChanges ?
            
            await context.Set<TEntity>().ToListAsync() :
            await context.Set<TEntity>().AsNoTracking().ToListAsync()
            ;

        public async Task<TEntity?> GetAsync(TKey key) 
            => await context.Set<TEntity>().FindAsync(key);

        public async Task<TEntity?> GetAsync(ISpecifications<TEntity> specifications) =>
            await SpecificationsEvaluator.CreateQuery(context.Set<TEntity>(),
                specifications).FirstOrDefaultAsync();
            
        

        public async Task<IEnumerable<TEntity>> GetAllAsync(ISpecifications<TEntity> specifications)
         => await SpecificationsEvaluator.CreateQuery(context.Set<TEntity>(),
                specifications).ToListAsync();

        public async Task<int> CountAsync(ISpecifications<TEntity> specifications)
         => await SpecificationsEvaluator.CreateQuery(context.Set<TEntity>(),
                specifications).CountAsync();
    }
}
