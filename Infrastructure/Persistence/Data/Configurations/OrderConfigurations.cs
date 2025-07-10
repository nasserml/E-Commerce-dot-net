
global using Order = Domain.Models.OrderModels.Order;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Persistence.Data.Configurations
{
    internal class OrderConfigurations : IEntityTypeConfiguration<Order>
    {
        public void Configure(EntityTypeBuilder<Order> builder)
        {
            builder.ToTable("Orders");
            builder.Property(d => d.SubTotal)
                .HasColumnType("decimal(8,2)");

            builder.HasMany(o => o.Items)
                .WithOne()
                .OnDelete(DeleteBehavior.Cascade);

            builder.OwnsOne(x=> x.ShipToAddress, x=> x.WithOwner());

        }
    }
}
