
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Persistence.Data.Configurations
{
    internal class OrderItemsConfigurations : IEntityTypeConfiguration<OrderItem>
    {
        public void Configure(EntityTypeBuilder<OrderItem> builder)
        {
            builder.ToTable("OrderItems");
            builder.Property(d => d.Price)
                .HasColumnType("decimal(8,2)");

            builder.OwnsOne(x => x.Product, x => x.WithOwner());
        }
    }
}
