# AskAT&T API Integration Guide

This document explains how the application integrates with the real AskAT&T API using Azure AD OAuth2 authentication.

## Overview

The application supports two modes for AskAT&T:
- **Mock Mode** (`USE_MOCK_ASKATT=true`): Uses simulated responses for local development
- **Production Mode** (`USE_MOCK_ASKATT=false`): Connects to real AskAT&T API with Azure AD authentication

## Azure AD OAuth2 Configuration

### Credentials

The following credentials are configured in `.env`:

```bash
# Azure AD OAuth2 Configuration
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_SECRET_ID=your-secret-id-here
```

### OAuth2 Flow

The app uses **Client Credentials Grant** flow:

1. **Token Request** to Azure AD:
   - URL: `https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token`
   - Method: POST
   - Content-Type: application/x-www-form-urlencoded

2. **Request Payload**:
   ```
   client_id={CLIENT_ID}
   client_secret={CLIENT_SECRET}
   scope={SCOPE}
   grant_type=client_credentials
   ```

3. **Available Scopes**:
   - **General QnA**: `api://your-api-id-here/.default`
   - **Domain QnA**: `api://your-api-id-here/.default`

   **IMPORTANT:** Client credential flows MUST use the `/.default` suffix. Azure AD will return error AADSTS1002012 if you try to use a specific scope like `.DomainQnA` without the `/.default` suffix.

4. **Response**:
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "Bearer",
     "expires_in": 3599
   }
   ```

## AskAT&T API Configuration

### API Endpoints

```bash
# AskAT&T API Configuration
ASKATT_API_BASE_URL_STAGE=https://your-api-gateway-url/stage/domain-services/chat-generativeai
ASKATT_API_BASE_URL_PRODUCTION=https://your-api-gateway-url/prod/domain-services/chat-generativeai

ASKATT_DOMAIN_NAME=GenerativeAI
ASKATT_MODEL_NAME=gpt-4o
ASKATT_MAX_TOKENS=800
```

### API Request Format

**Endpoint**: `POST /domain-services/chat-generativeai`

**Headers**:
```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

**Request Body**:
```json
{
  "domainName": "GenerativeAI",
  "modelName": "gpt-4o",
  "modelPayload": {
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Your question here"
          }
        ]
      }
    ],
    "max_completion_tokens": 800
  }
}
```

**Response Formats** (Dual Format Support):

The service supports both response formats for backward compatibility:

**Format 1: Real AskAT&T API Response** (Primary):
```json
{
  "status": "success",
  "modelResult": {
    "content": "The AI response text",
    "response_metadata": {
      "token_usage": {
        "prompt_tokens": 10,
        "completion_tokens": 50,
        "total_tokens": 60
      },
      "model_name": "gpt-4o-2024-08-06",
      "finish_reason": "stop"
    }
  }
}
```

**Format 2: OpenAI-like Response** (Fallback):
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "The AI response text"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

**Implementation Note**: The service first checks for the real API format (`status` + `modelResult`), then falls back to the OpenAI-like format (`choices` array) if not found. This ensures compatibility with both mock services and real API responses.

## Implementation Details

### Azure AD Service (`app/services/azure_ad.py`)

```python
from app.services.azure_ad import get_askatt_token

# Get token for general QnA (default)
token = await get_askatt_token(use_domain_scope=False)

# Get token for domain QnA
token = await get_askatt_token(use_domain_scope=True)
```

### AskAT&T Service (`app/services/askatt.py`)

The real AskAT&T service:
1. Obtains Azure AD token automatically
2. Formats conversation history according to API spec
3. Makes POST request to AskAT&T API
4. Parses response (supports both real API and OpenAI-like formats)
5. Streams response back to client in SSE format token-by-token

**Response Parsing Logic** (backend/app/services/askatt.py:96-142):
- **Primary**: Checks for `{"status": "success", "modelResult": {...}}` format
- **Fallback**: If not found, checks for `{"choices": [...]}` OpenAI-like format
- **Token Extraction**: Streams content character by character for real-time display
- **Usage Data**: Extracts from `response_metadata.token_usage` or `usage` object

### Chat Endpoint (`app/api/v1/chat.py`)

The `/api/v1/chat/askatt` endpoint automatically selects:
- **Mock service** when `USE_MOCK_ASKATT=true`
- **Real service** when `USE_MOCK_ASKATT=false`

## Switching Between Mock and Production

### Using Mock (Local Development)

1. Set in `.env`:
   ```
   USE_MOCK_ASKATT=true
   ```

2. No Azure AD authentication required
3. Returns simulated GPT-4 responses instantly

### Using Production (Real API)

1. Set in `.env`:
   ```
   USE_MOCK_ASKATT=false
   ```

2. Ensure Azure AD credentials are correct
3. Application will:
   - Automatically obtain Azure AD token
   - Call real AskAT&T API
   - Return actual GPT-4o responses

## Conversation History Format

The service maintains conversation context by sending previous messages:

```python
conversation_history = [
    {"role": "user", "content": "What is AT&T?"},
    {"role": "assistant", "content": "AT&T is a telecommunications company..."},
    {"role": "user", "content": "Tell me more"}  # New message
]
```

This gets formatted to match AskAT&T API format:

```json
{
  "messages": [
    {
      "role": "user",
      "content": [{"type": "text", "text": "What is AT&T?"}]
    },
    {
      "role": "assistant",
      "content": [{"type": "text", "text": "AT&T is a telecommunications company..."}]
    },
    {
      "role": "user",
      "content": [{"type": "text", "text": "Tell me more"}]
    }
  ]
}
```

## Error Handling

The service handles:

1. **Authentication Errors**:
   - Invalid credentials
   - Expired tokens
   - Scope issues

2. **API Errors**:
   - HTTP status errors (4xx, 5xx)
   - Timeout errors
   - Invalid response format

3. **Network Errors**:
   - Connection failures
   - SSL certificate issues (disabled verify for development)

All errors are returned as SSE error events:
```
data: {"type": "error", "content": "Error description"}
```

## Testing the Integration

### Test Authentication

```bash
cd backend
./venv/Scripts/python.exe -c "
import asyncio
from app.services.azure_ad import get_askatt_token

async def test():
    token = await get_askatt_token()
    print(f'Token: {token[:50]}...')

asyncio.run(test())
"
```

### Test API Call

```bash
curl -X POST http://localhost:8000/api/v1/chat/askatt \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}' \
  --no-buffer
```

## Security Considerations

1. **SSL Verification**: Currently disabled (`verify=False`) for development. Enable in production!
2. **Token Caching**: Tokens are cached in memory but not persisted
3. **Secrets Management**: Store credentials securely, not in version control
4. **Scope Selection**: Use appropriate scope based on use case

## Troubleshooting

### "Authentication failed" Error

- Check Azure AD credentials in `.env`
- Verify tenant ID, client ID, and client secret
- Check network access to Azure AD

### "API error: 401"

- Token might be expired or invalid
- Check scope matches API requirements
- Verify client has permission to access API

### "API error: 403"

- Client may not have permission
- Check API subscription/access rights

### "Timeout" Errors

- API may be slow to respond
- Increase timeout in `askatt.py`
- Check network connectivity

## Code References

- Azure AD Service: `backend/app/services/azure_ad.py`
- AskAT&T Service: `backend/app/services/askatt.py`
- Chat Endpoint: `backend/app/api/v1/chat.py:43-152`
- Configuration: `backend/app/config.py:25-41`
- Environment Variables: `backend/.env:18-35`
