using Shared.DataTransferObjects.Products;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Shared.DataTransferObjects
{
    public record PaginationResponse<TData>(int PageIndex, int PageSize, int Count, IEnumerable<TData> Data);
 
}
