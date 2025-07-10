using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace Shared.ErrorModels
{
    public class ErrorDetails
    {
        public int StatusCode { get; set; }
        public string Message { get; set; } = string.Empty;
        public string ErrorMessage { get; set; }

        public List<string>? Errors { get; set; }

        public override string ToString() => JsonSerializer.Serialize(this);
        
    }
}
