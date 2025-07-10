
using Domain.Contracts;

using E_Commerce.Web.Extensions;
using E_Commerce.Web.Factories;
using E_Commerce.Web.Middlewares;

using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

using Persistence;
using Persistence.Data;
using Persistence.Repositories;

using Services;

using ServicesAbstractions;

using Shared.ErrorModels;

using Swashbuckle.AspNetCore.SwaggerUI;

using System.Threading.Tasks;

namespace E_Commerce.Web
{
    public class Program
    {
        public static async Task Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);



            builder.Services.AddCors(options=>
            {
                options.AddPolicy("AllowAll", builder =>
                {
                    builder.AllowAnyOrigin()
                    .AllowAnyMethod()
                    .AllowAnyHeader();
                });
            });

          
            builder.Services.AddApplicationServices(builder.Configuration);
            builder.Services.AddInfrastructureServices(builder.Configuration);
            builder.Services.AddWebApplicationsServices(builder.Configuration);
        
         
            var app = builder.Build();

            await app.InitializeDataBaseAsync();
            

            
            app.UseCustomExceptionMiddleware();

          
            // Configure the HTTP request pipeline.
            if (app.Environment.IsDevelopment())
            {
                app.UseSwagger();
                app.UseSwaggerUI(options =>
                {
                    options.DocumentTitle = "My E-Commerce API";
                    options.DocExpansion(DocExpansion.None);

                    options.EnableFilter();
                    options.DisplayRequestDuration();
                    

                });
            }

            app.UseStaticFiles();
            app.UseHttpsRedirection();

            app.UseCors("AllowAll");
            app.UseAuthentication();
            app.UseAuthorization();

            //app.UseAuthorization();


            app.MapControllers();

            app.Run();
        }

        
    }
}
