using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Services
{
    public static class ApplicationServicesRegistration
    {
        /// <summary>
        /// Adds AutoMapper Services
        /// Adds UserManager Services
        /// </summary>
        /// <param name="services"></param>
        /// <returns></returns>
        public static IServiceCollection AddApplicationServices(this IServiceCollection services, IConfiguration configuration )
        {

            services.AddAutoMapper(typeof(Services.AssemblyReference).Assembly);
            //services.AddScoped<IServiceManager, ServiceManager>();
            services.AddScoped<IServiceManager, ServiceManagerWithFactoryDelegate>();

            // services
            services.AddScoped<IProductService, ProductService>();
            services.AddScoped<IAuthenticationService, AuthenticationService>();
            services.AddScoped<IBasketService, BasketService>();
            services.AddScoped<IOrderService, OrderService>();
            services.AddScoped<IPaymentService, PaymentService>();
            services.AddScoped<ICashService, CashService>();

            // Factory Delegate Registration
            services.AddScoped<Func<IProductService>>(provider=> ()=>
            provider.GetRequiredService<IProductService>());

            services.AddScoped<Func<IAuthenticationService>>(provider => () =>
           provider.GetRequiredService<IAuthenticationService>());

            services.AddScoped<Func<IBasketService>>(provider => () =>
           provider.GetRequiredService<IBasketService>());

            services.AddScoped<Func<IOrderService>>(provider => () =>
           provider.GetRequiredService<IOrderService>());

            services.AddScoped<Func<IPaymentService>>(provider => () =>
            provider.GetRequiredService<IPaymentService>());

            services.Configure<JWTOptions>(configuration.GetSection("JWTOptions"));

            return services;
        }
    }
}
