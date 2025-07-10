using Domain.Exceptions;

using Shared.ErrorModels;

using System.Net;
using System.Text.Json;

namespace E_Commerce.Web.Middlewares
{
    public class CustomExceptionHandlerMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly ILogger<CustomExceptionHandlerMiddleware> _logger;

        public CustomExceptionHandlerMiddleware(RequestDelegate next, ILogger<CustomExceptionHandlerMiddleware> logger)
        {
            _next = next;
            _logger = logger;
        }

        public async Task InvokeAsync(HttpContext httpContext)
        {
            try
            {
                await _next.Invoke(httpContext);

                await HandleNotFoundPathAsync(httpContext);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Something went wrong");

                await HandleExceptionAsunc(httpContext, ex);
            }
        }

        private static async Task HandleExceptionAsunc(HttpContext httpContext, Exception ex)
        {
            // set status code
            //httpContext.Response.StatusCode = (int)HttpStatusCode.InternalServerError ;

            // Set Content Type
            httpContext.Response.ContentType = "application/json";
            // Response Object
            var response = new ErrorDetails
            {

                ErrorMessage = ex.Message
            };
            response.StatusCode = ex switch
            {
                NotFoundException => StatusCodes.Status404NotFound,
                UnauthorizedException => StatusCodes.Status401Unauthorized,
                BadRequestException badRequestException => GetValidationErrors(badRequestException, response),
                _ => StatusCodes.Status500InternalServerError,
            };

            httpContext.Response.StatusCode = response.StatusCode;

            await httpContext.Response.WriteAsJsonAsync(response);
        }

        private static int GetValidationErrors(BadRequestException badRequestException, ErrorDetails response)
        {
            response.Errors = badRequestException.Errors;
            return StatusCodes.Status400BadRequest;
        }

        private static async Task HandleNotFoundPathAsync (HttpContext httpContext)
        {
            // logic 
            if (httpContext.Response.StatusCode == (int)HttpStatusCode.NotFound)
            {
                httpContext.Response.ContentType = "application/json";
                var response = new ErrorDetails
                {
                    ErrorMessage = $"Path {httpContext.Request.Path} Not Found",
                    StatusCode = StatusCodes.Status404NotFound
                };
                await httpContext.Response.WriteAsJsonAsync(response);

            }
        }
    }

    public static class CustomExceptionHandlerMiddlewareExtensions
    {
        public static IApplicationBuilder UseCustomExceptionMiddleware(this IApplicationBuilder app)
        {
            app.UseMiddleware<CustomExceptionHandlerMiddleware>();
            return app;
        }
    }
}
