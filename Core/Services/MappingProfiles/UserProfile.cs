using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Services.MappingProfiles
{
    internal class UserProfile : Profile
    {
        public UserProfile()
        {
            CreateMap<AddressDTO, Address>().ReverseMap();
        }
    }
}
