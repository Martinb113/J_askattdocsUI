# Environment Configuration Guide

## 🎯 Purpose

Keep the **same code** on both machines, but different **configurations**.

**Key Principle:** Code is in Git, configuration is in `.env` files (NOT in Git).

---

## 📁 Environment File Structure

```
backend/
  .env                    # Your actual config (NEVER commit)
  .env.example           # Template (safe to commit)
  .env.internal.example  # Internal server template (safe to commit)
```

---

## 🔧 Configuration Files

### `.env.example` (External/Development)

Template for your personal development PC:

```bash
# Application Environment
ENVIRONMENT=development

# Server URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Database (lightweight for development)
DATABASE_URL=sqlite:///./askdocs.db

# Authentication (mock for development)
USE_MOCK_AZURE_AD=true
AZURE_AD_TENANT_ID=mock-tenant-id
AZURE_AD_CLIENT_ID=mock-client-id
AZURE_AD_CLIENT_SECRET=mock-secret

# Services (mock for development)
USE_MOCK_ASKDOCS=true
USE_MOCK_ASKATT=true

# Security (development key - not sensitive)
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=DEBUG
```

### `.env.internal.example` (Internal/Production)

Template for company server:

```bash
# Application Environment
ENVIRONMENT=internal

# Server URLs (company internal)
BACKEND_URL=http://internal-server.company.local:8000
FRONTEND_URL=http://internal-server.company.local:5173

# Database (production PostgreSQL)
DATABASE_URL=postgresql://user:password@db-server.company.local:5432/askdocs

# Authentication (real company Azure AD)
USE_MOCK_AZURE_AD=false
AZURE_AD_TENANT_ID=your-company-tenant-id
AZURE_AD_CLIENT_ID=your-company-client-id
AZURE_AD_CLIENT_SECRET=your-company-client-secret

# Services (real company APIs)
USE_MOCK_ASKDOCS=false
USE_MOCK_ASKATT=false
ASKDOCS_API_URL=http://askdocs-api.company.local
ASKATT_API_URL=http://askatt-api.company.local

# Security (production secret - CHANGE THIS!)
SECRET_KEY=generate-a-strong-random-key-here
ALLOWED_ORIGINS=http://internal-server.company.local:5173

# Logging
LOG_LEVEL=INFO
```

---

## 🚀 Setup Process

### On External PC:

```bash
# Copy the development template
cp backend/.env.example backend/.env

# Edit for your local setup
nano backend/.env  # or your preferred editor

# Customize as needed for your PC
# (usually the defaults work fine)
```

### On Internal Server:

```bash
# Copy the internal template
cp backend/.env.internal.example backend/.env

# Edit with PRODUCTION values
nano backend/.env

# IMPORTANT: Use real credentials here
# - Real database connection string
# - Real Azure AD credentials  
# - Real API URLs
# - Strong SECRET_KEY
```

---

## 🔐 Generating Secure Values

### SECRET_KEY

```bash
# Generate a secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
# k2xB9vQ7nR4mL8pW5tY3sH6gF1jD0cA7

# Use this in .env:
SECRET_KEY=k2xB9vQ7nR4mL8pW5tY3sH6gF1jD0cA7
```

### Database Password

```bash
# Generate secure database password
python -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)))"
```

---

## 🎛️ How Code Uses Environment Variables

### In Python (FastAPI):

```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    backend_url: str
    database_url: str
    azure_ad_tenant_id: str
    use_mock_azure_ad: bool = True
    secret_key: str
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()

# Use in your code:
if settings.use_mock_azure_ad:
    # Use mock authentication
else:
    # Use real Azure AD
```

### In TypeScript (Frontend):

```typescript
// frontend/src/config.ts
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  environment: import.meta.env.VITE_ENVIRONMENT || 'development',
};

// Use in your code:
const response = await fetch(`${config.apiUrl}/api/v1/chat`);
```

---

## 🔄 Environment-Specific Code Patterns

### Good Pattern: Configuration-Driven

```python
# Uses environment variable to determine behavior
if settings.environment == "internal":
    # Production logic
    api_client = RealAPIClient(settings.api_url)
else:
    # Development logic
    api_client = MockAPIClient()
```

### Bad Pattern: Hardcoded

```python
# DON'T DO THIS - hardcoded values
api_url = "http://company-internal.local"
```

### Good Pattern: Feature Flags

```python
# Use boolean flags from .env
if settings.use_mock_askdocs:
    return mock_askdocs_response()
else:
    return real_askdocs_api_call()
```

---

## 📊 Environment Comparison

| Aspect | External (Dev) | Internal (Prod) |
|--------|---------------|-----------------|
| **Purpose** | Development & Testing | Production |
| **Database** | SQLite (simple) | PostgreSQL (robust) |
| **Auth** | Mock | Real Azure AD |
| **APIs** | Mock responses | Real company APIs |
| **Logging** | DEBUG (verbose) | INFO (essential) |
| **Secret Key** | Simple dev key | Strong random key |
| **Data** | Test/fake data | Real company data |
| **Safety** | Can break/test freely | Must be stable |

---

## 🚨 Critical Rules

### NEVER Commit:
❌ `.env` (actual configuration)  
❌ `.env.production`  
❌ `.env.local`  
❌ `.env.internal` (if you name it this)  

### SAFE to Commit:
✅ `.env.example` (template with fake values)  
✅ `.env.internal.example` (template with fake values)  
✅ Code that reads from environment variables  

---

## 🔍 Verifying Configuration

### Check .env is Not Tracked:

```bash
# Should NOT show .env file
git status

# If it shows .env:
git rm --cached backend/.env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Ensure .env is ignored"
```

### Check Configuration is Loaded:

```python
# Add to your app for debugging (remove in production)
@app.on_event("startup")
async def startup_event():
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Using mock Azure AD: {settings.use_mock_azure_ad}")
    logger.info(f"Database: {settings.database_url.split('@')[0]}...")  # Don't log full URL
```

---

## 🔄 Updating Configuration

### Add New Setting:

1. **Add to both .env.example files:**
```bash
# backend/.env.example
NEW_FEATURE_ENABLED=false

# backend/.env.internal.example  
NEW_FEATURE_ENABLED=true
```

2. **Update your .env files locally** (both machines)

3. **Update code to use it:**
```python
class Settings(BaseSettings):
    new_feature_enabled: bool = False
```

4. **Commit the examples:**
```bash
git add backend/.env.example backend/.env.internal.example
git commit -m "Add NEW_FEATURE_ENABLED configuration option"
git push origin develop
```

5. **On other machine, update .env** based on new .env.example

---

## 🆘 Troubleshooting

### "Configuration not loading"

```bash
# Check .env file exists
ls backend/.env

# Check file has correct values
cat backend/.env

# Check app is looking in right place
# In Python, BaseSettings looks for .env in current directory
```

### "Wrong environment used"

```python
# Add debug logging
print(f"Current environment: {settings.environment}")
print(f"Loaded from: {settings.Config.env_file}")
```

### "Database connection fails on Internal"

```bash
# Test database connection separately
psql -h db-server.company.local -U user -d askdocs

# Check firewall/network
ping db-server.company.local

# Verify DATABASE_URL format
# postgresql://username:password@host:port/database
```

---

## 📋 Configuration Checklist

When setting up new environment:

- [ ] Copy appropriate .env.example to .env
- [ ] Update all placeholder values
- [ ] Generate secure SECRET_KEY
- [ ] Set correct ENVIRONMENT value
- [ ] Configure database connection
- [ ] Set authentication settings
- [ ] Update API URLs
- [ ] Test application starts
- [ ] Verify .env not tracked by git

---

**Remember:** Same code everywhere, different configurations in `.env` files. This keeps your codebase clean and your sensitive data safe.

