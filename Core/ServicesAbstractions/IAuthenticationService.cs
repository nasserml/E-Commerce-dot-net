using Shared.Authentication;

namespace ServicesAbstractions
{
    public interface IAuthenticationService
    {
        // [HttpPost]
        // Login (LoginRequest{string email, string Password})
        // => UserResponse {string Token, string Email, string DisplayName}
        Task<UserResponse> LoginAsync(LoginRequest request);


        // [HttpPost]
        // Register(RegisterRequest{string Email, string UserName, string Password, string DisplayName})
        // => UserResponse {string Token, string Email, string DisplayName}
        Task<UserResponse> RegisterAsync(RegisterRequest request);

        // CheckEmail(string email) => bool
        Task<bool> CheckEmailAsync(string email);

        // GetCurrentUserAddress(AddressDTO ) => AddressDTO
        Task<AddressDTO> GetUserAddressAsync(string email);

        // UpdateCurrentUserAddress(AddressDTO) => AddressDTO
        Task<AddressDTO> UpdateUserAddressAsync(AddressDTO addressDTO,string email);

        //GetCurrentUser() =>
        // UserResponse {string Token, string Email, string DisplayName}
        Task<UserResponse> GetUserByEmail(string email);


    }
}
