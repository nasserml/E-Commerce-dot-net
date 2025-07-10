using Domain.Models;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Domain.Contracts
{
    public interface IUnitOfWork
    {
        Task<int> SaveChangesAsync();


        //IGenericRepository<Product, int> Products { get; set; }
        //IGenericRepository<ProductType, int> ProductTypes { get; set; }
        //IGenericRepository<ProductBrand, int> ProductBrands { get; set; }

        IGenericRepository<TEntity, TKey> GetRepository<TEntity, TKey>()
            where TEntity : BaseEntity<TKey>;

        IGenericRepository<TEntity, int> GetRepository<TEntity>()
            where TEntity : BaseEntity<int>;

    }
}
