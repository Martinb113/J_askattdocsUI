# AskDocs API Integration Guide

This document explains how the application integrates with the real AskDocs API using Azure AD OAuth2 authentication (same as AskAT&T).

## Overview

The application supports two modes for AskDocs:
- **Mock Mode** (`USE_MOCK_ASKDOCS=true`): Uses simulated RAG responses for local development
- **Production Mode** (`USE_MOCK_ASKDOCS=false`): Connects to real AskDocs API with Azure AD authentication

## Azure AD OAuth2 Configuration

### Shared Authentication with AskAT&T

AskDocs uses the **same Azure AD authentication** as AskAT&T. The credentials are already configured:

```bash
# Azure AD OAuth2 Configuration (shared with AskAT&T)
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_SCOPE_ASKATT_DOMAIN=api://your-api-id/.default
```

### OAuth2 Flow

Same as AskAT&T, using **Client Credentials Grant** flow:

1. **Token Request** to Azure AD
2. **Scope**: Uses domain scope (`/.default` suffix required)
3. **Token obtained** via `get_askatt_token(use_domain_scope=True)`

See [ASKATT_INTEGRATION.md](./ASKATT_INTEGRATION.md) for complete Azure AD details.

## AskDocs API Configuration

### API Endpoints

```bash
# AskDocs API Configuration
ASKDOCS_API_BASE_URL_STAGE=https://your-api-gateway-url/stage/askdocs/query
ASKDOCS_API_BASE_URL_PRODUCTION=https://your-api-gateway-url/prod/askdocs/query
```

### API Request Format

**Endpoint**: `POST /askdocs/query`

**Headers**:
```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

**Request Body**:
```json
{
  "domain": "SD_International",
  "config_version": "sim_wiki_con_v1v1",
  "query": "Your question here"
}
```

**Parameters**:
- `domain`: Domain key from configuration (e.g., "SD_International", "att_support")
- `config_version`: Configuration key (e.g., "sim_wiki_con_v1v1", "ois_wiki_com_v1v1")
- `query`: User's question

**Response Formats** (Dual Format Support):

The service supports both response formats for backward compatibility:

**Format 1: Real AskDocs API Response with Citations** (Primary):
```json
{
  "response": "The AI answer text with RAG context",
  "citations": [
    {
      "id": "doc-123",
      "metadata": {
        "source": "https://internal-docs/article-123",
        "chunk_id": 1,
        "captions": {
          "text": "Service Information Management documentation",
          "highlights": "SIM configuration details"
        }
      },
      "page_content": "Full content of the relevant document chunk...",
      "type": "Document",
      "aisearch_score": 0.95,
      "aisearch_reranker_score": 0.88
    }
  ],
  "usage": {
    "total_tokens": 350,
    "prompt_tokens": 150,
    "completion_tokens": 200
  },
  "question": "How do I reset my password?",
  "refactor_question": null,
  "chat_history": [],
  "aicache": false,
  "total_latency": 2.5
}
```

**Format 2: Simple Sources Response** (Fallback):
```json
{
  "response": "The AI answer text with RAG context",
  "sources": [
    {
      "title": "Source Document Title",
      "url": "https://internal-docs/article-123"
    },
    {
      "title": "Another Source",
      "url": "https://internal-wiki/page-456"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  }
}
```

**Alternative Response Keys** (also supported):
- `answer` instead of `response`
- `content` instead of `response`

**Implementation Note**: The service first checks for `citations` array (real API format), extracting title from `metadata.captions.text` or `page_content`. If not found, it falls back to the `sources` array format. Both formats are converted to a unified sources array for the frontend.

## Implementation Details

### Azure AD Service (`app/services/azure_ad.py`)

AskDocs reuses the existing Azure AD service:

```python
from app.services.azure_ad import get_askatt_token

# Get token for AskDocs (domain scope)
token = await get_askatt_token(use_domain_scope=True)
```

### AskDocs Service (`app/services/askdocs.py`)

The real AskDocs service:
1. Obtains Azure AD token automatically (domain scope)
2. Fetches configuration details (domain_key, config_key)
3. Formats request with domain, config_version, and query
4. Makes POST request to AskDocs API
5. Parses response (supports both citations and sources formats)
6. Streams response back to client in SSE format token-by-token
7. Includes source attribution from RAG (citations or sources)

**Citation Parsing Logic** (backend/app/services/askdocs.py:109-145):
- **Primary**: Checks for `citations` array with metadata and captions
- **Fallback**: If not found, checks for `sources` array
- **Title Extraction**:
  - From `metadata.captions.text` (first 100 chars)
  - Or from `page_content` (first 100 chars)
  - Or from `citation.id` as fallback
- **Unified Output**: Both formats converted to `{"title": "...", "url": "..."}` array

### Chat Endpoint (`app/api/v1/chat.py:159-289`)

The `/api/v1/chat/askdocs` endpoint automatically selects:
- **Mock service** when `USE_MOCK_ASKDOCS=true`
- **Real service** when `USE_MOCK_ASKDOCS=false`

## Switching Between Mock and Production

### Using Mock (Local Development)

1. Set in `.env`:
   ```
   USE_MOCK_ASKDOCS=true
   ```

2. No Azure AD authentication required
3. Returns simulated RAG responses instantly
4. Uses mock domain configurations (SD_International, att_support)

### Using Production (Real API)

1. Set in `.env`:
   ```
   USE_MOCK_ASKDOCS=false
   ```

2. Ensure Azure AD credentials are correct (shared with AskAT&T)
3. Configure AskDocs API URL
4. Application will:
   - Automatically obtain Azure AD token (domain scope)
   - Call real AskDocs API with domain and config
   - Return actual RAG responses with sources

## Domain and Configuration

### Configuration Structure

Each AskDocs configuration has:
- **Domain**: High-level category (e.g., "SD_International")
- **Config Key**: Specific configuration version (e.g., "sim_wiki_con_v1v1")
- **Environment**: "stage" or "production"

### Example Configurations

**SD_International Domain**:
- `sim_wiki_con_v1v1` - SIM Wiki Configuration v1.1
- `ois_wiki_com_v1v1` - OIS Wiki Configuration v1.1

These map to specific knowledge bases in the AskDocs system.

## Conversation History Format

The service does **not** currently send conversation history to AskDocs API:

```python
# Future enhancement: include conversation context
# Currently only sends current message
payload = {
    "domain": config.domain.domain_key,
    "config_version": config.config_key,
    "query": message  # Only current question
}
```

**Note**: If AskDocs API supports conversation history, the implementation can be enhanced similar to AskAT&T.

## Error Handling

The service handles:

1. **Authentication Errors**:
   - Invalid credentials
   - Expired tokens
   - Scope issues

2. **API Errors**:
   - HTTP status errors (4xx, 5xx)
   - Timeout errors (120s timeout)
   - Invalid response format

3. **Configuration Errors**:
   - Configuration not found
   - User doesn't have access to configuration
   - Domain/config mismatch

4. **Network Errors**:
   - Connection failures
   - SSL certificate issues (disabled verify for development)

All errors are returned as SSE error events:
```
data: {"type": "error", "content": "Error description"}
```

## Testing the Integration

### Test with Mock Mode

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123!"}'

# 2. Get configurations
curl -X GET http://localhost:8000/api/v1/chat/configurations \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Test AskDocs chat (replace configuration_id)
curl -X POST http://localhost:8000/api/v1/chat/askdocs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I reset my password?", "configuration_id": "UUID-HERE"}' \
  --no-buffer
```

### Test with Production Mode

1. Set `USE_MOCK_ASKDOCS=false` in `.env`
2. Configure `ASKDOCS_API_BASE_URL_PRODUCTION`
3. Restart backend server
4. Test via frontend or curl (same as above)

## Response Format

### SSE Event Types

**1. Conversation ID** (new conversations only):
```
data: {"type": "conversation_id", "conversation_id": "uuid-here"}
```

**2. Token** (streaming response):
```
data: {"type": "token", "content": "T"}
data: {"type": "token", "content": "h"}
data: {"type": "token", "content": "e"}
```

**3. Sources** (RAG attribution):
```
data: {"type": "sources", "sources": [
  {"title": "Source 1", "url": "https://..."},
  {"title": "Source 2", "url": "https://..."}
]}
```

**4. Usage** (token statistics):
```
data: {"type": "usage", "usage": {
  "prompt_tokens": 150,
  "completion_tokens": 200,
  "total_tokens": 350
}}
```

**5. End** (stream complete):
```
data: {"type": "end"}
```

**6. Error** (if something fails):
```
data: {"type": "error", "content": "Error message"}
```

## Security Considerations

1. **SSL Verification**: Currently disabled (`verify=False`) for development. Enable in production!
2. **Token Reuse**: Shares Azure AD tokens with AskAT&T (same authentication)
3. **Secrets Management**: Store credentials securely, not in version control
4. **Scope Selection**: Uses domain scope (`/.default` suffix required)
5. **Role-Based Access**: Configuration access controlled by user roles

## Troubleshooting

### "Configuration not found or access denied"

- Check user has appropriate role assigned
- Verify configuration_id is correct
- Check configuration is active (is_active=true)

### "Authentication failed" Error

- Same as AskAT&T - check Azure AD credentials
- Verify domain scope is correct
- Check network access to Azure AD

### "API error: 401"

- Token might be expired or invalid
- Check scope matches API requirements
- Verify client has permission to access AskDocs API

### "API error: 404"

- AskDocs API endpoint might be incorrect
- Check ASKDOCS_API_BASE_URL in `.env`
- Verify environment (stage vs production)

### "Timeout" Errors

- AskDocs API may be slow (RAG processing takes time)
- Current timeout: 120 seconds
- Check network connectivity

### "Unexpected response format"

- API response doesn't match expected format
- Check logs for actual response structure
- Verify API version compatibility

## Code References

- Azure AD Service: `backend/app/services/azure_ad.py`
- AskDocs Service: `backend/app/services/askdocs.py`
- AskDocs Mock Service: `backend/app/services/askdocs_mock.py`
- Chat Endpoint: `backend/app/api/v1/chat.py:159-289`
- Configuration: `backend/app/config.py:48-51`
- Environment Variables: `backend/.env:42-46`

## Comparison with AskAT&T

### Similarities

| Feature | AskAT&T | AskDocs |
|---------|---------|---------|
| Authentication | Azure AD OAuth2 | ✅ Same |
| Token Scope | `.default` suffix | ✅ Same |
| Streaming | SSE format | ✅ Same |
| Mock Mode | Supported | ✅ Supported |
| Error Handling | SSE error events | ✅ Same |

### Differences

| Feature | AskAT&T | AskDocs |
|---------|---------|---------|
| Purpose | General OpenAI chat | Domain-specific RAG |
| Request Format | Messages array | domain + config_version + query |
| Response | Plain text | Text + sources |
| Conversation History | ✅ Sent | ❌ Not yet (future enhancement) |
| Configuration | Global settings | Per-user role-based configs |
| Timeout | 60 seconds | 120 seconds |

## Future Enhancements

1. **Conversation History**: Add support for sending previous messages to AskDocs API
2. **Streaming Responses**: If AskDocs API supports SSE, stream tokens in real-time
3. **Source Enrichment**: Add more source metadata (page numbers, relevance scores)
4. **Caching**: Cache RAG results for frequently asked questions
5. **Analytics**: Track most-used configurations and domains

## Related Documentation

- [ASKATT_INTEGRATION.md](./ASKATT_INTEGRATION.md) - AskAT&T integration (shares authentication)
- [MOCK_CONFIGURATION_GUIDE.md](./MOCK_CONFIGURATION_GUIDE.md) - Mock configuration details
- [SECURITY.md](./SECURITY.md) - Security guidelines
- [README.md](./README.md) - Backend setup and configuration

---

**Last Updated**: 2025-10-20
**Status**: ✅ Implemented with dual format support, ready for testing
