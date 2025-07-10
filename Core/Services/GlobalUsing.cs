global using AutoMapper;

global using Domain.Contracts;
global using Domain.Exceptions;
global using Domain.Models.Basket;
global using Domain.Models.Identity;
global using Domain.Models.OrderModels;
global using Domain.Models.Products;

global using Microsoft.AspNetCore.Identity;
global using Microsoft.Extensions.Options;
global using Microsoft.IdentityModel.Tokens;

global using Services.Specifications;

global using ServicesAbstractions;

global using Shared.Authentication;
global using Shared.DataTransferObjects;
global using Shared.DataTransferObjects.BasketItem;
global using Shared.DataTransferObjects.Products;

global using System.IdentityModel.Tokens.Jwt;
global using System.Linq.Expressions;
global using System.Security.Claims;
global using System.Text;
