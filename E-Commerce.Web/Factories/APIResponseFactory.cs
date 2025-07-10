using Azure;

using Microsoft.AspNetCore.Mvc;

using Shared.ErrorModels;

namespace E_Commerce.Web.Factories
{
    public static class APIResponseFactory
    {
        public static IActionResult GenerateAPIValidationResponse(ActionContext context) 
            {
              var errors = context.ModelState.Where(m => m.Value.Errors.Any())
                    .Select(m => new ValidationError
                    {
                        Field = m.Key,
                        Errors = m.Value.Errors.Select(error => error.ErrorMessage)
                    });

        var response = new ValidationErrorResponse { ValidationErrors = errors };
                    return new BadRequestObjectResult(response);

    }
    }
}
