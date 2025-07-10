
using Domain.Models.Identity;

using Microsoft.AspNetCore.Identity;

using Persistence.Identity;

using StackExchange.Redis;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Persistence
{
    public static class InfrastructureServicesRegistration
    {
        public static IServiceCollection AddInfrastructureServices(this IServiceCollection services,
            IConfiguration configuration)
        {
            services.AddScoped<IDbInitializer, DbInitializer>();
            services.AddDbContext<StoreDbContext>(options =>
            {
                var connectionString = configuration.GetConnectionString("DefaultConnection");
                options.UseSqlServer(connectionString);
            });

            services.AddDbContext<StoreIdentityDbContext>(options =>
            {
                var connectionString = configuration.GetConnectionString("IdentityConnection");
                options.UseSqlServer(connectionString);
            });


       
            services.AddSingleton<IConnectionMultiplexer>((_) =>
            {
                return ConnectionMultiplexer.Connect(configuration.GetConnectionString("RedisConnection"));
            });

            services.AddScoped<IBasketRepository, BasketRepository>();
            services.AddScoped<ICashRepository, CashRepository>();
            services.AddScoped<IUnitOfWork, UnitOfWork>();
            CongfigureIdentity(services, configuration);
            return services;
        }

        private static void CongfigureIdentity(IServiceCollection services, IConfiguration configuration)
        {
            services.AddIdentityCore<ApplicationUser>(config =>
            {
                config.User.RequireUniqueEmail = true;

                config.Password.RequiredLength = 8;
                config.Password.RequireNonAlphanumeric = false;
                config.Password.RequireUppercase = false;
                config.Password.RequireLowercase = false;
                config.Password.RequireDigit = false;

            }).AddRoles<IdentityRole>()
            .AddEntityFrameworkStores<StoreIdentityDbContext>()
                ;
        }
    }
}
