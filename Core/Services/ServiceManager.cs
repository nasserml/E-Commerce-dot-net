namespace Services
{
    public class ServiceManager(IMapper mapper, IUnitOfWork unitOfWork,
        IBasketRepository basketRepository,
        UserManager<ApplicationUser> userManager,
        IOptions<JWTOptions> options) 
        //:IServiceManager
    {
        private readonly Lazy<IProductService> _lazyProductService = 
            new Lazy<IProductService>(()=> new ProductService(unitOfWork, mapper));

        private readonly Lazy<IBasketService> _lazyBasketService =
            new Lazy<IBasketService>(() => new BasketService(basketRepository, mapper));

        private readonly Lazy<IAuthenticationService> _lazyAuthenticationServie =
            new(() => new AuthenticationService(userManager, options, mapper));

        private readonly Lazy<IOrderService> _lazyOrderService =
           new(() => new OrderService(mapper, unitOfWork, basketRepository));



        public IProductService ProductService => _lazyProductService.Value;

        public IBasketService BasketService => _lazyBasketService.Value;

        public IAuthenticationService AuthenticationService => _lazyAuthenticationServie.Value ;

        public IOrderService OrderService => _lazyOrderService.Value;
    }
}
