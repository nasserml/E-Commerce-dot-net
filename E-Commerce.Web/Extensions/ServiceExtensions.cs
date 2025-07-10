using Domain.Contracts;

using E_Commerce.Web.Factories;

using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;

using Shared.Authentication;

using System.Text;

namespace E_Commerce.Web.Extensions
{
    public static class ServiceExtensions
    {
        public static IServiceCollection AddSwaggerServices(this IServiceCollection services)
        {
            services.AddEndpointsApiExplorer();
            services.AddSwaggerGen(options =>
            {
                options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
                {
                    Name = "Authorization", 
                    In = ParameterLocation.Header,
                    Type = SecuritySchemeType.ApiKey,
                    Scheme = "Bearer",
                    Description= "JWT Authorization header using the bearer schema  'Bearer' space token"
                });

                options.AddSecurityRequirement(new OpenApiSecurityRequirement
                {
                    {
                        new OpenApiSecurityScheme
                        {
                            Reference = new OpenApiReference
                            {
                                Type = ReferenceType.SecurityScheme,
                                Id= "Bearer"
                            }
                        },
                        new List<string>()
                    }
                });
            });
            return services;
        }

    
        public static IServiceCollection AddWebApplicationsServices(this IServiceCollection services, 
            IConfiguration configuration)
        {
            services.AddControllers();
            services.Configure<ApiBehaviorOptions>(options =>
            {
                options.InvalidModelStateResponseFactory = APIResponseFactory.GenerateAPIValidationResponse;
            });
            services.AddSwaggerServices();
            ConfigureJwt(services, configuration);
            return services;

        }
    
        public static async Task<WebApplication> InitializeDataBaseAsync(this WebApplication app)
        {
       
            using var scope = app.Services.CreateScope();
            var dbInitializer = scope.ServiceProvider.GetRequiredService<IDbInitializer>();
            await dbInitializer.InitializeAsync();
            await dbInitializer.InitializeIdentityAsync();

            return app;
        
        }

        private static void ConfigureJwt(IServiceCollection services, IConfiguration configuration)
        {
            var jwt = configuration.GetSection("JWTOptions").Get<JWTOptions>();
            services.AddAuthentication(config =>
            {
                config.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                config.DefaultChallengeScheme  = JwtBearerDefaults.AuthenticationScheme;
            }).AddJwtBearer(config =>
            {
                config.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = true,
                    ValidIssuer = jwt.Issuer,

                    ValidateAudience = true,
                    ValidAudience = jwt.Audience,

                    ValidateLifetime = true,

                    ValidateIssuerSigningKey = true,
                    IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwt.SecretKey))

                };
            });


        }

    }
}
