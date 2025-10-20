# Security Guidelines

## Overview

This document outlines security best practices and considerations for the AI Chat Application backend.

## Credential Management

### ⚠️ CRITICAL: Never Commit Secrets to Version Control

**Protected Files:**
- `.env` - Contains actual credentials (in `.gitignore`)
- Any files with real API keys, passwords, or tokens

**Safe Files:**
- `.env.example` - Template with placeholder values
- Documentation files (ASKATT_INTEGRATION.md, etc.) - Use placeholder values only

### Configuration Files Status

| File | Status | Contains Real Credentials |
|------|--------|--------------------------|
| `.env` | ✅ Protected (in .gitignore) | YES - DO NOT COMMIT |
| `.env.example` | ✅ Safe to commit | NO - Placeholder values only |
| `app/config.py` | ✅ Safe to commit | NO - Reads from .env |
| `ASKATT_INTEGRATION.md` | ✅ Sanitized | NO - Uses placeholders |
| `ASKATT_TESTING.md` | ✅ Sanitized | NO - Uses placeholders |
| `README.md` | ✅ Safe | NO - Uses placeholders |

### Current Configuration State

**Real credentials are stored ONLY in:**
- `backend/.env` (which is in `.gitignore` and not committed)

**All documentation uses placeholder values:**
- `your-tenant-id-here`
- `your-client-id-here`
- `your-client-secret-here`
- `your-api-gateway-url`
- `{your-api-id}`
- `{tenant-id}`

## Azure AD OAuth2 Security

### Client Credentials

**Current Setup:**
- Grant Type: Client Credentials Flow
- Scope: `api://{api-id}/.default`
- Token Expiration: ~3599 seconds (1 hour)

**Security Considerations:**

1. **Scope Validation:** Client credential flows REQUIRE `/.default` suffix
   - ✅ Correct: `api://95273ce2-6fec-4001-9716-a209d398184f/.default`
   - ❌ Incorrect: `api://95273ce2-6fec-4001-9716-a209d398184f/.DomainQnA`

2. **Token Storage:** Tokens are currently cached in memory only
   - Not persisted to disk
   - Lost on application restart
   - Consider implementing proper token refresh for long-running sessions

3. **SSL Verification:** Currently DISABLED for development
   ```python
   # CURRENT (Development):
   async with httpx.AsyncClient(verify=False, timeout=60.0) as client:

   # PRODUCTION (Required):
   async with httpx.AsyncClient(verify=True, timeout=60.0) as client:
   ```

   **ACTION REQUIRED:** Enable SSL verification before production deployment

## API Security

### AskAT&T API

**Authentication:**
- Bearer token from Azure AD
- Token included in Authorization header
- Automatic token refresh on expiration

**Current Issues:**
- SSL certificate verification disabled (`verify=False`)
- Debug logging may expose sensitive data

**Required Changes for Production:**
1. Enable SSL verification: `verify=True`
2. Remove debug logging of tokens and payloads
3. Implement rate limiting
4. Add request timeout handling
5. Implement circuit breaker pattern for API failures

### Database Security

**Current Configuration:**
```python
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/askdocs_db
```

**Production Requirements:**
1. Use strong database password
2. Create dedicated database user with minimal privileges
3. Enable SSL/TLS for database connections
4. Restrict database access to application servers only
5. Regular security updates and patches

### JWT Authentication

**Current Configuration:**
```python
JWT_SECRET=ew1aTHWlJJ3uYtmsSNU0V4_w6lyWWu0kkfC4j4dzY6s
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8
```

**Security Requirements:**

1. **JWT Secret:**
   - Generate cryptographically secure secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - NEVER use default or example secrets in production
   - Rotate secrets periodically

2. **Token Expiration:**
   - Current: 8 hours
   - Consider shorter expiration for sensitive operations
   - Implement refresh token mechanism

3. **Token Storage:**
   - Frontend should store in httpOnly cookies (not localStorage)
   - Clear tokens on logout
   - Invalidate tokens on password change

## CORS Configuration

**Current Configuration:**
```python
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Production Requirements:**
1. Remove localhost origins
2. Add only production frontend URLs
3. Use HTTPS URLs only
4. Be specific - avoid wildcards (`*`)

**Example Production Configuration:**
```python
CORS_ORIGINS=https://app.yourcompany.com,https://admin.yourcompany.com
```

## Input Validation

**Current Protection:**
- Pydantic schemas validate all API inputs
- SQL injection protection via SQLAlchemy ORM
- XSS protection via JSON responses

**Message Length Limits:**
```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
```

**Additional Recommendations:**
1. Implement rate limiting per user
2. Add content filtering for inappropriate messages
3. Monitor for abuse patterns
4. Log suspicious activity

## Error Handling

**Current Implementation:**
- Errors returned as JSON
- Stack traces hidden in production (when `DEBUG=False`)
- SSE error events for streaming endpoints

**Security Concerns:**
1. Ensure error messages don't leak sensitive information
2. Log detailed errors server-side only
3. Return generic error messages to clients
4. Monitor error patterns for security issues

## Logging and Monitoring

**Current Logging:**
```python
LOG_LEVEL=INFO
DEBUG=True
```

**Production Requirements:**

1. **Set Appropriate Log Level:**
   ```python
   LOG_LEVEL=WARNING
   DEBUG=False
   ```

2. **Remove Debug Logging:**
   - Don't log tokens or credentials
   - Don't log full payloads with user data
   - Sanitize logs before storage

3. **Security Logging:**
   - Log all authentication attempts
   - Log authorization failures
   - Log API errors and rate limit violations
   - Monitor for suspicious patterns

4. **Log Storage:**
   - Secure log storage
   - Regular log rotation
   - Retain logs per compliance requirements

## Pre-Production Security Checklist

### Environment Configuration

- [ ] Change all default passwords
- [ ] Generate new JWT_SECRET
- [ ] Set `DEBUG=False`
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Update CORS_ORIGINS to production URLs only
- [ ] Enable SSL verification (`verify=True` in all httpx clients)

### Credentials Management

- [ ] Verify `.env` is in `.gitignore`
- [ ] Use secrets management system (Azure Key Vault, AWS Secrets Manager, etc.)
- [ ] Rotate all credentials from development
- [ ] Document credential rotation procedures

### Database Security

- [ ] Create dedicated database user with minimal privileges
- [ ] Use strong database password
- [ ] Enable SSL/TLS for database connections
- [ ] Configure connection pooling limits
- [ ] Set up database backups
- [ ] Enable audit logging

### API Security

- [ ] Enable SSL certificate verification
- [ ] Implement rate limiting
- [ ] Add request size limits
- [ ] Configure timeouts appropriately
- [ ] Implement circuit breaker for external APIs
- [ ] Set up API monitoring and alerting

### Code Security

- [ ] Remove all debug logging of sensitive data
- [ ] Review error messages for information disclosure
- [ ] Scan dependencies for vulnerabilities (`pip-audit`)
- [ ] Run security linters
- [ ] Code review with security focus

### Infrastructure Security

- [ ] Use HTTPS only
- [ ] Configure security headers (HSTS, CSP, etc.)
- [ ] Set up WAF (Web Application Firewall)
- [ ] Configure DDoS protection
- [ ] Restrict network access (firewall rules)
- [ ] Enable security monitoring

### Compliance and Documentation

- [ ] Document all security controls
- [ ] Create incident response plan
- [ ] Set up security logging and monitoring
- [ ] Review data handling compliance (GDPR, etc.)
- [ ] Document credential rotation procedures

## Known Security Issues

### Development Environment Issues

These are ACCEPTABLE for development but MUST be fixed for production:

1. **SSL Verification Disabled**
   - Location: `app/services/azure_ad.py:45`, `app/services/askatt.py:88`
   - Status: ⚠️ Development only
   - Action: Enable before production

2. **Debug Logging**
   - Location: Various service files
   - Status: ⚠️ Development only
   - Action: Remove sensitive data from logs

3. **Mock Mode Enabled**
   - Location: `.env` (`USE_MOCK_ASKATT=true`)
   - Status: ⚠️ Development only
   - Action: Set to `false` in production

## Security Incident Response

### If Credentials Are Compromised

1. **Immediate Actions:**
   - Rotate all compromised credentials
   - Revoke Azure AD client secrets
   - Change JWT_SECRET (invalidates all tokens)
   - Change database password
   - Review access logs for unauthorized access

2. **Investigation:**
   - Check git history for exposed secrets
   - Review recent commits and changes
   - Audit API access logs
   - Check for unusual database activity

3. **Remediation:**
   - Update all affected systems with new credentials
   - Force re-authentication of all users
   - Document incident and lessons learned
   - Review and improve credential management procedures

### If Repository Is Made Public Accidentally

1. **Immediate Actions:**
   - Make repository private immediately
   - Assume all credentials in commit history are compromised
   - Follow credential compromise procedures above

2. **GitHub-Specific:**
   - Request GitHub to purge cached versions
   - Use tools like `git-filter-repo` to remove sensitive data
   - Force push cleaned history
   - Notify all developers

## Security Contact

For security issues or questions:
1. Review this document and related security documentation
2. Check Azure AD portal for authentication issues
3. Contact security team for incidents or concerns

## References

- [Azure AD OAuth2 Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)

## Version History

- 2025-10-18: Initial security documentation created
- Added Azure AD scope requirements (/.default suffix)
- Documented current security state and requirements
