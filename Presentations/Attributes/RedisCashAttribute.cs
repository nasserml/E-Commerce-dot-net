using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.Extensions.DependencyInjection;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Presentations.Attributes
{
    internal class RedisCashAttribute(int durationInSec = 90)
        //: Attribute, IAsyncActionFilter
    : ActionFilterAttribute
    {
        public override async Task OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)
        {
            var service = context.HttpContext.RequestServices.GetRequiredService<ICashService>();
            // Create cash key
            string cashKey = CreateCashKey(context.HttpContext.Request);
            // search with key
            var cashValue = await service.GetAsync(cashKey);

            // value
            if(cashValue != null)
            {
                // return from cash
                context.Result = new ContentResult
                {
                    Content = cashValue,
                    ContentType = "application/json",
                    StatusCode = StatusCodes.Status200OK
                };
                return;
            }
            // value => null
            // invoke
            var executedContext = await next.Invoke();
            if (executedContext.Result is OkObjectResult result)
                await service.SetAsync(cashKey, result.Value, 
                    TimeSpan.FromSeconds(durationInSec));

            // set Cash
            
        }

        private static string CreateCashKey(HttpRequest request)
        {
            StringBuilder builder = new();

            builder.Append(request.Path + '?');

            foreach (var item in request.Query.OrderBy(q => q.Key))
                builder.Append($"{item.Key}={item.Value}&");
            return builder.ToString().Trim('&');
           
        }
    }
}
