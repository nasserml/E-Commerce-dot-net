using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Shared.Authentication
{
    public class JWTOptions
    {
        public string SecretKey { get; set; }
        public string Issuer { get; set; }
        public string Audience { get; set; }
        public double DurationInDays { get; set; }
    }
}

//"JWTOptions": {
//    "SecretKey": "NnyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9=",
//    "Issuer": "https://localhost:7222",
//    "Audience": "https://localhost:4200",
//    "DurationInDays":  7

//  }
