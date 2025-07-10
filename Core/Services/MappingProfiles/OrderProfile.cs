using Domain.Models.OrderModels;

using Microsoft.Extensions.Configuration;

using Shared.Orders;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Services.MappingProfiles
{
    internal class OrderProfile: Profile
    {
        public OrderProfile()
        {
            CreateMap<OrderAddress, AddressDTO>().ReverseMap();

            CreateMap<OrderItem, OrderItemDTO>()
                .ForMember(d => d.ProductName, o => o.MapFrom(s => s.Product.ProductName))
                .ForMember(d => d.ProductId, o => o.MapFrom(s => s.Product.ProductId))
                .ForMember(d => d.PictureUrl,
                o => o.MapFrom<OrderItemPictureUrlResolver>());

            CreateMap<Order, OrderResponse>()
                .ForMember(d=>d.DeliveryMethod,
                o=> o.MapFrom(s=>s.DeliveryMethod.ShortName ))
                .ForMember(d=>d.DeliveryCost,
                o=> o.MapFrom(s=>s.DeliveryMethod.Cost ))
                .ForMember(d => d.Total,
                o => o.MapFrom(s => s.DeliveryMethod.Cost + s.SubTotal));

            CreateMap<DeliveryMethod, DeliveryMethodResponse>();

        }
    }

    internal class OrderItemPictureUrlResolver(IConfiguration configuration)
        : IValueResolver<OrderItem, OrderItemDTO, string>
    {
        public string Resolve(OrderItem source, OrderItemDTO destination, string destMember, ResolutionContext context)
        => string.IsNullOrWhiteSpace(source.Product.PictureUrl) ? string.Empty :
            $"{configuration["BaseUrl"]}{source.Product.PictureUrl}";
    }
}
