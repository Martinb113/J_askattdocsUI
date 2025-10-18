# Environment Setup Guide

**Purpose**: Configure `.env` files for different environments  
**Security**: .env files are NEVER committed to Git

---

## 🎯 Overview

This application uses environment variables to handle configuration differences between:
- **External PC**: Development environment with mock services
- **Internal Server**: Production environment with real company resources

The same codebase runs in both environments - only the `.env` file differs.

---

## 📁 File Structure

```
j_askdocs/
├── backend/
│   ├── .env                    # ❌ NEVER COMMIT (in .gitignore)
│   ├── .env.example            # ✅ Safe template for external
│   └── .env.internal.example   # ✅ Safe template for internal
├── frontend/
│   └── (frontend uses backend URLs via API calls)
└── .gitignore                  # Contains .env patterns
```

---

## 🔧 Setup Instructions

### **For External PC (Development)**

#### **Step 1: Create .env file**

```bash
# Navigate to backend folder
cd C:\Users\admin\Documents\AI_projects\j_askdocs\backend

# Copy the example template
copy .env.example .env

# Open in your editor
notepad .env
# Or: code .env (if using VS Code)
```

#### **Step 2: Configure for Development**

Edit `backend/.env` with development settings:

```bash
# =============================================================================
# EXTERNAL PC - DEVELOPMENT CONFIGURATION
# =============================================================================

# Application Environment
ENVIRONMENT=development

# Backend Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Database (SQLite for development - no server needed)
DATABASE_URL=sqlite:///./askdocs.db

# Authentication - MOCK MODE for development
USE_MOCK_AZURE_AD=true
AZURE_AD_TENANT_ID=mock-tenant-id
AZURE_AD_CLIENT_ID=mock-client-id
AZURE_AD_CLIENT_SECRET=mock-secret

# Services - MOCK MODE for development
USE_MOCK_ASKDOCS=true
USE_MOCK_ASKATT=true
ASKDOCS_API_URL=http://mock-askdocs.local
ASKATT_API_URL=http://mock-askatt.local

# Security
SECRET_KEY=development-secret-key-change-me-123456789
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:5174

# Logging
LOG_LEVEL=DEBUG

# Development Flags
DEBUG=true
RELOAD=true
```

#### **Step 3: Verify Setup**

```bash
# Check that .env exists
dir .env

# Verify it's in .gitignore (won't show in git status)
git status
# .env should NOT appear in the list

# Verify it's being ignored
git check-ignore .env
# Should output: .env
```

---

### **For Internal Server (Production)**

#### **Step 1: Create .env file**

```bash
# Navigate to backend folder
cd /path/to/j_askdocs/backend

# Copy the internal example template
cp .env.internal.example .env

# Open in your editor
nano .env
# Or: vim .env
```

#### **Step 2: Configure for Production**

Edit `backend/.env` with **REAL COMPANY CREDENTIALS**:

⚠️ **WARNING**: The values below are EXAMPLES. Replace with actual company values!

```bash
# =============================================================================
# INTERNAL SERVER - PRODUCTION CONFIGURATION
# =============================================================================
# ⚠️ THIS FILE CONTAINS SENSITIVE COMPANY DATA
# ⚠️ NEVER COMMIT THIS FILE TO GIT
# ⚠️ NEVER SHARE CONTENTS OF THIS FILE
# =============================================================================

# Application Environment
ENVIRONMENT=production

# Backend Configuration (Internal Server URLs)
BACKEND_URL=http://internal-server.company.local:8000
FRONTEND_URL=http://internal-server.company.local:5173

# Database (Real PostgreSQL)
# Replace with actual company database credentials
DATABASE_URL=postgresql://dbuser:STRONG_PASSWORD@db-server.company.local:5432/askdocs

# Authentication - REAL Azure AD
USE_MOCK_AZURE_AD=false
AZURE_AD_TENANT_ID=12345678-abcd-efgh-ijkl-mnopqrstuvwx
AZURE_AD_CLIENT_ID=87654321-zyxw-vuts-rqpo-nmlkjihgfedcba
AZURE_AD_CLIENT_SECRET=ACTUAL_COMPANY_SECRET_HERE

# Services - REAL Company APIs
USE_MOCK_ASKDOCS=false
USE_MOCK_ASKATT=false
ASKDOCS_API_URL=http://askdocs-api.company.local
ASKATT_API_URL=http://askatt-api.company.local

# Security
# Generate a strong secret key: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=CHANGE_THIS_TO_STRONG_RANDOM_SECRET_KEY
ALLOWED_ORIGINS=http://internal-server.company.local:5173,http://internal-server.company.local:3000

# Logging
LOG_LEVEL=INFO

# Production Flags
DEBUG=false
RELOAD=false

# Internal Company Specific
COMPANY_DOMAIN=company.local
INTERNAL_API_KEY=company_internal_api_key_here
```

#### **Step 3: Secure the File**

```bash
# Set strict file permissions (Linux/Unix)
chmod 600 .env
# Now only you can read/write this file

# Verify it's not tracked by Git
git status
# .env should NOT appear

# NEVER add this file to Git
# If asked, always answer NO when git asks to add .env
```

---

## 🔐 Environment Variables Reference

### **Core Application Settings**

| Variable | Purpose | External Value | Internal Value |
|----------|---------|----------------|----------------|
| `ENVIRONMENT` | Identifies environment | `development` | `production` |
| `DEBUG` | Enable debug mode | `true` | `false` |
| `LOG_LEVEL` | Logging verbosity | `DEBUG` | `INFO` or `WARNING` |

### **URLs and Endpoints**

| Variable | Purpose | External Value | Internal Value |
|----------|---------|----------------|----------------|
| `BACKEND_URL` | Backend API URL | `http://localhost:8000` | Company internal URL |
| `FRONTEND_URL` | Frontend app URL | `http://localhost:5173` | Company internal URL |
| `ALLOWED_ORIGINS` | CORS allowed origins | `localhost:*` | Company domains |

### **Database Configuration**

| Variable | Purpose | External Value | Internal Value |
|----------|---------|----------------|----------------|
| `DATABASE_URL` | Database connection | `sqlite:///./askdocs.db` | PostgreSQL connection string |

**Database URL Format**:
```bash
# SQLite (External - Development)
sqlite:///./askdocs.db

# PostgreSQL (Internal - Production)
postgresql://username:password@host:port/database

# Examples:
postgresql://askdocs_user:SecurePass123@db.company.local:5432/askdocs_prod
```

### **Authentication (Azure AD)**

| Variable | Purpose | External Value | Internal Value |
|----------|---------|----------------|----------------|
| `USE_MOCK_AZURE_AD` | Use mock authentication | `true` | `false` |
| `AZURE_AD_TENANT_ID` | Azure AD tenant ID | `mock-value` | Real tenant ID |
| `AZURE_AD_CLIENT_ID` | Azure AD application ID | `mock-value` | Real client ID |
| `AZURE_AD_CLIENT_SECRET` | Azure AD secret | `mock-value` | Real secret |

**Finding Azure AD Values** (Internal Server):
1. Go to Azure Portal: https://portal.azure.com
2. Navigate to "Azure Active Directory"
3. Select "App registrations"
4. Find your application
5. Copy Tenant ID and Client ID
6. Generate new secret under "Certificates & secrets"

### **External Services**

| Variable | Purpose | External Value | Internal Value |
|----------|---------|----------------|----------------|
| `USE_MOCK_ASKDOCS` | Use mock AskDocs service | `true` | `false` |
| `USE_MOCK_ASKATT` | Use mock AskAtt service | `true` | `false` |
| `ASKDOCS_API_URL` | AskDocs API endpoint | `http://mock...` | Real internal API |
| `ASKATT_API_URL` | AskAtt API endpoint | `http://mock...` | Real internal API |

### **Security Settings**

| Variable | Purpose | External Value | Internal Value |
|----------|---------|----------------|----------------|
| `SECRET_KEY` | JWT signing key | Simple dev key | Strong random key |

**Generating a Strong Secret Key**:
```bash
# Python method (recommended)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Output example:
# xK7_9mPqL2wRn5vB8cH4jF1sG6tN3oY0eU

# Use this output as your SECRET_KEY
```

---

## 🔄 How Configuration Works in Code

### **Loading Environment Variables**

The application uses `pydantic-settings` to load configuration:

```python
# backend/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class automatically loads values from .env file or environment.
    Each variable defined here can be overridden via .env file.
    """
    
    # Application environment
    environment: str = "development"
    
    # Database
    database_url: str
    
    # Azure AD
    use_mock_azure_ad: bool = True
    azure_ad_tenant_id: str
    azure_ad_client_id: str
    azure_ad_client_secret: str
    
    # Services
    use_mock_askdocs: bool = True
    use_mock_askatt: bool = True
    
    class Config:
        env_file = ".env"  # Automatically loads from .env
        case_sensitive = False  # DATABASE_URL = database_url

# Create global settings instance
settings = Settings()
```

### **Using Settings in Code**

```python
# In any file that needs configuration

from app.config import settings

# Example: Check environment
if settings.environment == "production":
    # Use production logic
    use_real_authentication()
else:
    # Use development logic
    use_mock_authentication()

# Example: Conditional service usage
if settings.use_mock_askdocs:
    service = MockAskDocsService()
else:
    service = RealAskDocsService(settings.askdocs_api_url)
```

### **Environment-Specific Behavior**

```python
# backend/app/services/auth.py

from app.config import settings

def authenticate_user(token: str):
    """
    Authenticates user with Azure AD or mock depending on configuration.
    
    Same code works in both environments - behavior changes based on .env
    """
    if settings.use_mock_azure_ad:
        # Development: Use mock authentication
        return mock_azure_ad.validate_token(token)
    else:
        # Production: Use real Azure AD
        return real_azure_ad.validate_token(
            token,
            tenant_id=settings.azure_ad_tenant_id,
            client_id=settings.azure_ad_client_id
        )
```

---

## 🧪 Testing Your Configuration

### **External PC (Development)**

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Check logs - should show:
# INFO: Environment: development
# INFO: Using mock Azure AD: True
# INFO: Using mock AskDocs: True

# Test authentication
# Should work with any username/password (mock mode)

# Test database
# Should create askdocs.db file in backend folder
```

### **Internal Server (Production)**

```bash
# Start backend
cd backend
uvicorn app.main:app

# Check logs - should show:
# INFO: Environment: production
# INFO: Using mock Azure AD: False
# INFO: Connected to database: postgresql://...

# Test authentication
# Should require real company Azure AD login

# Test database
# Should connect to company PostgreSQL server
```

---

## 🚨 Common Issues and Solutions

### **Issue 1: "Configuration not found" or "Settings validation error"**

**Cause**: Missing .env file or missing required variables

**Solution**:
```bash
# Check if .env exists
ls -la backend/.env

# If missing, create from template
cp backend/.env.example backend/.env

# Edit with required values
nano backend/.env
```

### **Issue 2: "Database connection failed"**

**Cause**: Incorrect DATABASE_URL in .env

**Solution**:
```bash
# For External (SQLite)
DATABASE_URL=sqlite:///./askdocs.db

# For Internal (PostgreSQL) - verify credentials
DATABASE_URL=postgresql://user:password@host:5432/database

# Test database connection
cd backend
python -c "from app.database import engine; print('Connected!' if engine else 'Failed')"
```

### **Issue 3: ".env file was committed to Git!"**

**Cause**: .env not in .gitignore, or forced addition

**Solution**:
```bash
# Remove from Git tracking (file stays on disk)
git rm --cached backend/.env

# Make sure .gitignore contains .env
echo "backend/.env" >> .gitignore
echo ".env" >> .gitignore

# Commit the removal
git commit -m "Remove .env from version control"

# If sensitive data was pushed, see SAFETY_CHECKLIST.md
```

### **Issue 4: "Application using wrong environment"**

**Cause**: .env file in wrong location or not being loaded

**Solution**:
```bash
# .env must be in backend/ folder, next to main.py
backend/
├── .env          # <-- Should be here
├── app/
│   └── main.py
└── ...

# Check if file is being loaded
cd backend
python -c "from app.config import settings; print(settings.environment)"
# Should print: development or production
```

### **Issue 5: "Environment variables not updating"**

**Cause**: Application caching old values, needs restart

**Solution**:
```bash
# Stop the application (Ctrl+C)
# Edit .env file
# Restart the application
uvicorn app.main:app --reload
```

---

## 📋 Environment Setup Checklist

### **External PC Setup**
- [ ] Navigate to backend folder
- [ ] Copy `.env.example` to `.env`
- [ ] Edit `.env` with development settings
- [ ] Verify `.env` is not tracked by Git: `git status`
- [ ] Set `ENVIRONMENT=development`
- [ ] Set `USE_MOCK_AZURE_AD=true`
- [ ] Set `DATABASE_URL=sqlite:///./askdocs.db`
- [ ] Test application starts correctly
- [ ] Verify mock services are being used

### **Internal Server Setup**
- [ ] Navigate to backend folder
- [ ] Copy `.env.internal.example` to `.env`
- [ ] Edit `.env` with **REAL** company credentials
- [ ] Set strict file permissions: `chmod 600 .env`
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `USE_MOCK_AZURE_AD=false`
- [ ] Configure real `AZURE_AD_*` values
- [ ] Configure real `DATABASE_URL` (PostgreSQL)
- [ ] Configure real API endpoints
- [ ] Generate strong `SECRET_KEY`
- [ ] Verify `.env` is not tracked by Git: `git status`
- [ ] Test application starts correctly
- [ ] Test real Azure AD authentication
- [ ] Test database connectivity

---

## 🔒 Security Reminders

1. **NEVER** commit `.env` files to Git
2. **NEVER** share `.env` file contents in chat/email/tickets
3. **NEVER** copy production `.env` to external PC
4. **ALWAYS** use different `SECRET_KEY` in each environment
5. **ALWAYS** verify `.env` is in `.gitignore`
6. **ALWAYS** use strong passwords for production database
7. **ALWAYS** review `git status` before committing

---

## 📚 Additional Resources

- [12-Factor App Config](https://12factor.net/config) - Environment configuration best practices
- [Pydantic Settings Docs](https://docs.pydantic.dev/latest/usage/settings/) - How pydantic loads .env
- [Environment Variables Security](https://www.doppler.com/blog/environment-variables-security) - Security best practices

---

**Next Steps**: See [SAFETY_CHECKLIST.md](SAFETY_CHECKLIST.md) for security verification before pushing to GitHub

