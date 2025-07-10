global using Microsoft.AspNetCore.Mvc;
global using ServicesAbstractions;
global using Shared.DataTransferObjects.BasketItem;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;

namespace Presentations.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public abstract class APIController: ControllerBase
    {
        protected string GetEmailFromToken() => User.FindFirstValue(ClaimTypes.Email)!;

        
    }
}
