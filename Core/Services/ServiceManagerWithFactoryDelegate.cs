namespace Services
{
    internal class ServiceManagerWithFactoryDelegate(Func<IProductService> productFactory,
        Func<IAuthenticationService> authFactory,
        Func<IOrderService> orderDactory,
        Func<IBasketService> basketFactory,
        Func<IPaymentService> paymentFactory
        )
        : IServiceManager
    {
        public IProductService ProductService => productFactory.Invoke();

        public IBasketService BasketService => basketFactory.Invoke();

        public IAuthenticationService AuthenticationService => authFactory.Invoke();

        public IOrderService OrderService => orderDactory.Invoke();

        public IPaymentService PaymentService => paymentFactory.Invoke();
    }
}
