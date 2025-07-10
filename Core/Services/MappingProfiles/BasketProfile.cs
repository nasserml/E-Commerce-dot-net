
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Services.MappingProfiles
{
    internal class BasketProfile : Profile
    {
        public BasketProfile()
        {
            CreateMap<CustomerBasket, BasketDTO>().ReverseMap();
            CreateMap<BasketItem, BasketItemDTO>().ReverseMap();
        }
    }
}
