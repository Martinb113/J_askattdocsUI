# AskAT&T Integration Testing Guide

This document provides a comprehensive testing guide for the AskAT&T API integration with Azure AD OAuth2 authentication.

## Testing Summary

### ✅ Tests Completed Successfully

1. **Azure AD Authentication**
   - ✅ General scope token acquisition (`/.default`)
   - ✅ Domain scope token acquisition (`/.default`)
   - ✅ Token format validation (JWT)
   - ✅ Error handling for invalid scopes

2. **Configuration**
   - ✅ Environment variables loaded correctly
   - ✅ Settings class properly configured
   - ✅ Mock/Production mode switching implemented

3. **Service Implementation**
   - ✅ Azure AD service created (`app/services/azure_ad.py`)
   - ✅ AskAT&T service created (`app/services/askatt.py`)
   - ✅ Chat endpoint updated to use real service

### ⚠️ Tests Pending (Requires Network Access)

The following tests require access to the AskAT&T API endpoints and should be performed when connected to the appropriate network:

1. **Real AskAT&T API Call**
2. **SSE Streaming Response**
3. **Conversation History Handling**
4. **Error Handling for API Failures**

## Test Results

### 1. Azure AD Token Acquisition Test

**Test Date:** 2025-10-18

**Test Script:**
```python
import asyncio
from app.services.azure_ad import get_askatt_token

async def test():
    # Test general scope
    token = await get_askatt_token(use_domain_scope=False)
    print(f'Token: {token[:50]}...')

    # Test domain scope
    domain_token = await get_askatt_token(use_domain_scope=True)
    print(f'Domain token: {domain_token[:50]}...')

asyncio.run(test())
```

**Results:**
```
1. General scope token:
   Successfully obtained token
   Token (first 50 chars): eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InlFVX...
   Token length: 1288 characters

2. Domain scope token:
   Successfully obtained domain token
   Domain token (first 50 chars): eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InlFVX...
   Token length: 1283 characters

==> Azure AD authentication: SUCCESS
```

**Key Finding:** Azure AD client credential flows require `/.default` suffix. Using `.DomainQnA` without `/.default` results in error `AADSTS1002012`.

### 2. Configuration Validation Test

**Environment Variables Verified:**
```bash
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_AUTH_URL=https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
AZURE_SCOPE_ASKATT_GENERAL=api://your-api-id-here/.default
AZURE_SCOPE_ASKATT_DOMAIN=api://your-api-id-here/.default
ASKATT_API_BASE_URL_STAGE=https://your-api-gateway-url/stage/domain-services/chat-generativeai
ASKATT_API_BASE_URL_PRODUCTION=https://your-api-gateway-url/prod/domain-services/chat-generativeai
ASKATT_DOMAIN_NAME=GenerativeAI
ASKATT_MODEL_NAME=gpt-4o
ASKATT_MAX_TOKENS=800
```

**Result:** ✅ All configuration loaded successfully

## Testing with Real AskAT&T API

### Prerequisites

1. **Network Access:** Must be connected to network with access to:
   - Azure AD: `login.microsoftonline.com`
   - AskAT&T API: `your-api-gateway-url`

2. **Environment Configuration:**
   ```bash
   USE_MOCK_ASKATT=false  # Switch to production mode
   ```

3. **Valid Credentials:** Ensure Azure AD credentials have not expired

### Test Procedure

#### Step 1: Switch to Production Mode

Edit `backend/.env`:
```bash
USE_MOCK_ASKATT=false
```

Restart the backend server to load new settings.

#### Step 2: Test with curl

**Get JWT Token:**
```bash
# Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123!"}'

# Response will contain: {"access_token": "eyJ...", "token_type": "bearer"}
# Save the access_token for next step
```

**Test AskAT&T Chat:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/askatt \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AT&T?"}' \
  --no-buffer
```

**Expected Response (SSE Format):**
```
data: {"type": "conversation_id", "conversation_id": "uuid-here"}

data: {"type": "token", "content": "A"}

data: {"type": "token", "content": "T"}

data: {"type": "token", "content": "&"}

data: {"type": "token", "content": "T"}

...

data: {"type": "usage", "usage": {"prompt_tokens": 10, "completion_tokens": 50, "total_tokens": 60}}

data: {"type": "end"}
```

#### Step 3: Test with Frontend

1. Open `http://localhost:3000`
2. Login with `admin` / `Admin123!`
3. Click "Ask AT&T"
4. Send a message: "Hello, how are you?"
5. Verify streaming response appears token-by-token

#### Step 4: Test Conversation History

1. Continue the conversation from Step 3
2. Send follow-up message: "Tell me more"
3. Verify the AI has context from previous messages

#### Step 5: Test Error Handling

**Test Authentication Failure:**
```bash
# Temporarily set invalid credentials in .env
AZURE_CLIENT_SECRET=invalid_secret

# Restart server and attempt chat
# Expected: Error message about authentication failure
```

**Test Network Timeout:**
```bash
# Set very short timeout in askatt.py (e.g., timeout=0.1)
# Expected: Timeout error returned to client
```

## Mock vs. Production Mode

### Mock Mode (Current Default)

**Settings:**
```bash
USE_MOCK_ASKATT=true
```

**Behavior:**
- Uses `app/services/askatt_mock.py`
- Returns simulated GPT-4 responses
- No network calls to Azure AD or AskAT&T API
- Instant responses (no real AI processing)

**Use Cases:**
- Local development without network access
- Frontend UI testing
- Rapid iteration

### Production Mode

**Settings:**
```bash
USE_MOCK_ASKATT=false
```

**Behavior:**
- Uses `app/services/askatt.py`
- Obtains real Azure AD token
- Calls real AskAT&T API
- Returns actual GPT-4o responses
- Network-dependent

**Use Cases:**
- Integration testing
- Production deployment
- Real user interactions

## Known Issues and Resolutions

### Issue 1: AADSTS1002012 - Invalid Scope

**Error:**
```
Client credential flows must have a scope value with /.default suffixed to the resource identifier
```

**Resolution:**
- Changed `AZURE_SCOPE_ASKATT_DOMAIN` from `.DomainQnA` to `.default`
- Updated both `.env` and `config.py`
- Both scopes now use `/.default` suffix

### Issue 2: SSL Certificate Verification Disabled

**Current Setting:**
```python
async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
```

**Security Note:** SSL verification is currently disabled for development. This should be enabled in production:
```python
async with httpx.AsyncClient(verify=True, timeout=60.0) as client:
```

## Test Checklist

### Before Production Deployment

- [ ] Test Azure AD token acquisition on production network
- [ ] Test AskAT&T API call with real network access
- [ ] Verify SSE streaming works end-to-end
- [ ] Test conversation history handling
- [ ] Test error scenarios (auth failure, network timeout, API errors)
- [ ] Enable SSL certificate verification (`verify=True`)
- [ ] Remove debug logging of sensitive data
- [ ] Test with multiple concurrent users
- [ ] Verify token caching works correctly
- [ ] Test token expiration handling (tokens expire after 3599 seconds)

### Security Checklist

- [ ] Ensure credentials are not committed to version control
- [ ] Use environment variables for all secrets
- [ ] Enable SSL certificate verification
- [ ] Implement token refresh logic for long-running sessions
- [ ] Add rate limiting for API calls
- [ ] Log security events (failed auth, etc.)
- [ ] Review CORS settings for production

## Troubleshooting

### Authentication Errors

**Symptom:** `data: {"type": "error", "content": "Authentication failed"}`

**Checks:**
1. Verify Azure AD credentials in `.env`
2. Check network connectivity to `login.microsoftonline.com`
3. Verify tenant ID is correct
4. Check client secret hasn't expired

**Debug:**
```python
# Add to azure_ad.py temporarily
logger.setLevel(logging.DEBUG)
logger.debug(f"Token request payload: {payload}")
logger.debug(f"Token response: {response.text}")
```

### API Call Errors

**Symptom:** `data: {"type": "error", "content": "API error: 401"}`

**Checks:**
1. Token might be expired or invalid
2. Verify token is being sent in Authorization header
3. Check API subscription/access rights

**Symptom:** `data: {"type": "error", "content": "API error: 403"}`

**Checks:**
1. Client may not have permission to access AskAT&T API
2. Verify API subscription is active
3. Check scope is correct

**Symptom:** Timeout errors

**Checks:**
1. Network connectivity to API endpoint
2. Increase timeout in `askatt.py` if needed
3. Check API endpoint URL is correct

### Streaming Issues

**Symptom:** No tokens received, just end event

**Checks:**
1. Verify API response format matches expected structure
2. Check `choices` array exists in response
3. Review response parsing logic in `askatt.py`

**Debug:**
```python
# Add to askatt.py temporarily
logger.debug(f"API Response: {json.dumps(result, indent=2)}")
```

## Next Steps

1. **Complete Network Testing:** When on appropriate network, run full test procedure
2. **Frontend Integration:** Verify frontend displays responses correctly
3. **Error Handling:** Test all error scenarios
4. **Performance Testing:** Test with concurrent users
5. **Security Review:** Implement production security checklist
6. **Documentation:** Update user-facing documentation

## Contact

For issues or questions about AskAT&T integration:
- Check logs in backend console for detailed error messages
- Review Azure AD portal for authentication issues
- Contact API team for AskAT&T endpoint access issues

## Code References

- Azure AD Service: `backend/app/services/azure_ad.py`
- AskAT&T Service: `backend/app/services/askatt.py`
- Mock Service: `backend/app/services/askatt_mock.py`
- Chat Endpoint: `backend/app/api/v1/chat.py:45-156`
- Configuration: `backend/app/config.py:25-41`
- Environment: `backend/.env:18-35`
- Integration Guide: `backend/ASKATT_INTEGRATION.md`
