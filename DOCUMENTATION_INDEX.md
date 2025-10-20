# Documentation Index

This document provides an overview of all documentation files in the AI Chat Application project.

## Quick Start

1. **Setup:** [backend/README.md](backend/README.md) - Complete setup and installation guide
2. **Configuration:** [backend/.env.example](backend/.env.example) - Environment variable template
3. **Security:** [backend/SECURITY.md](backend/SECURITY.md) - Security guidelines and checklist
4. **What's New:** [CHANGELOG.md](CHANGELOG.md) - Recent changes and updates

## Backend Documentation

### Core Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [backend/README.md](backend/README.md) | Complete backend guide with setup, configuration, and architecture | All developers |
| [backend/.env.example](backend/.env.example) | Environment variable template with placeholders | All developers |

### API Integration Guides

| Document | Description | Status |
|----------|-------------|--------|
| [backend/ASKATT_INTEGRATION.md](backend/ASKATT_INTEGRATION.md) | AskAT&T API integration with Azure AD OAuth2 | ✅ Complete |
| [backend/ASKATT_TESTING.md](backend/ASKATT_TESTING.md) | Testing guide with procedures and results | ✅ Tested (Auth layer) |
| [backend/ASKDOCS_API_INTEGRATION.md](backend/ASKDOCS_API_INTEGRATION.md) | AskDocs RAG API integration with Azure AD OAuth2 | ✅ Complete |
| [backend/MOCK_CONFIGURATION_GUIDE.md](backend/MOCK_CONFIGURATION_GUIDE.md) | Mock configuration system for AskDocs | ✅ Complete |

### Security Documentation

| Document | Description | Importance |
|----------|-------------|-----------|
| [backend/SECURITY.md](backend/SECURITY.md) | Security guidelines and pre-production checklist | 🔴 CRITICAL |
| [.gitignore](.gitignore) | Git ignore rules protecting credentials | 🔴 CRITICAL |

## Configuration Files

### Environment Configuration

| File | Purpose | Safety Status |
|------|---------|--------------|
| `backend/.env` | **REAL credentials** - DO NOT COMMIT | 🔴 Protected by .gitignore |
| `backend/.env.example` | Template with placeholders | ✅ Safe to commit |

### Application Configuration

| File | Purpose | Contains Secrets |
|------|---------|-----------------|
| `backend/app/config.py` | Settings class (reads from .env) | ❌ No - Safe to commit |

## API Documentation

### Interactive API Docs

When backend server is running:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

#### Chat Services
- `POST /api/v1/chat/askatt` - AskAT&T chat (general AI)
- `POST /api/v1/chat/askdocs` - AskDocs chat (domain-specific RAG)
- `GET /api/v1/chat/conversations` - List conversations
- `GET /api/v1/chat/conversations/{id}` - Get conversation details
- `DELETE /api/v1/chat/conversations/{id}` - Delete conversation

#### Configuration
- `GET /api/v1/chat/configurations` - List AskDocs configurations (role-based)
- `POST /api/v1/chat/messages/{id}/feedback` - Submit message feedback

## Recent Improvements (2025-10-20)

### Dual Response Format Support

Both AskAT&T and AskDocs services now support multiple response formats for maximum compatibility:

**AskAT&T Dual Format Support:**
- **Primary**: Real API format with `{"status": "success", "modelResult": {...}}`
- **Fallback**: OpenAI-like format with `{"choices": [...]}`
- **Location**: `backend/app/services/askatt.py:96-142`
- **Benefits**: Works with both real API and mock services seamlessly

**AskDocs Citations Parsing:**
- **Primary**: Citations array with complex metadata structure
- **Fallback**: Simple sources array
- **Location**: `backend/app/services/askdocs.py:109-145`
- **Benefits**: Extracts meaningful titles from citations, handles real API response format

**Why This Matters:**
- **Backward Compatibility**: Works with existing mock services
- **Production Ready**: Handles real API responses correctly
- **No Breaking Changes**: Existing code continues to work
- **Better UX**: Real-time token streaming from actual APIs

## Key Concepts

### Mock vs. Production Mode

The application supports two operation modes:

**Mock Mode (Development):**
```bash
USE_MOCK_ASKATT=true
USE_MOCK_ASKDOCS=true
```
- No network dependencies
- Instant responses
- Realistic test data
- No credentials required

**Production Mode:**
```bash
USE_MOCK_ASKATT=false
USE_MOCK_ASKDOCS=false
```
- Real Azure AD authentication
- Real API calls to AskAT&T/AskDocs
- Network access required
- Valid credentials required

### Azure AD OAuth2 Integration

**Key Requirement:** Client credential flows MUST use `/.default` suffix for scopes.

✅ **Correct:**
```
api://95273ce2-6fec-4001-9716-a209d398184f/.default
```

❌ **Incorrect:**
```
api://95273ce2-6fec-4001-9716-a209d398184f/.DomainQnA
```

See [ASKATT_INTEGRATION.md](backend/ASKATT_INTEGRATION.md) for complete details.

## Security Information

### ⚠️ CRITICAL: Credential Protection

**Files with Real Credentials:**
- `backend/.env` - Protected by `.gitignore` (DO NOT COMMIT)

**Files Safe to Commit:**
- `backend/.env.example` - Placeholder values only
- All documentation files - Sanitized with placeholders
- `backend/app/config.py` - Reads from .env, no hardcoded secrets

### Git Protection Status

✅ `.env` file is protected by `.gitignore` at line 33:
```
backend/.env
```

Verify protection:
```bash
git check-ignore -v backend/.env
# Output: .gitignore:33:backend/.env	backend/.env
```

### Pre-Production Security Checklist

Before deploying to production, review [SECURITY.md](backend/SECURITY.md) and complete:

- [ ] Change all default passwords
- [ ] Generate new JWT_SECRET
- [ ] Set DEBUG=False
- [ ] Enable SSL verification (verify=True)
- [ ] Update CORS_ORIGINS to production URLs
- [ ] Rotate all development credentials
- [ ] Use secrets management system
- [ ] Review complete security checklist

## Testing Status

### Completed Tests

✅ **Azure AD Authentication**
- General scope token acquisition - SUCCESS
- Domain scope token acquisition - SUCCESS
- Token format validation (JWT) - SUCCESS
- Scope requirement discovered (/.default) - DOCUMENTED

✅ **Mock Configuration**
- SD_International domain - SUCCESS
- sim_wiki_con_v1v1 config - SUCCESS
- ois_wiki_com_v1v1 config - SUCCESS

✅ **Configuration Loading**
- All environment variables - SUCCESS
- Settings class initialization - SUCCESS
- Mock/Production mode switching - SUCCESS

### Pending Tests

⚠️ **Requires Network Access:**
- Real AskAT&T API call
- SSE streaming response
- Conversation history handling
- Error scenarios (timeout, auth failure, etc.)

See [ASKATT_TESTING.md](backend/ASKATT_TESTING.md) for complete test procedures.

## Architecture Overview

### Service Flow

```
User Request
    ↓
FastAPI Backend
    ↓
JWT Authentication
    ↓
    ├─→ AskAT&T Chat ─→ Mock Service (USE_MOCK_ASKATT=true)
    │                 └─→ Azure AD + AskAT&T API (USE_MOCK_ASKATT=false)
    │
    └─→ AskDocs Chat ─→ Mock Service (USE_MOCK_ASKDOCS=true)
                      └─→ AskDocs API (USE_MOCK_ASKDOCS=false)
```

### Technology Stack

**Backend:**
- FastAPI (async web framework)
- PostgreSQL + AsyncPG (database)
- SQLAlchemy 2.0 (async ORM)
- JWT (authentication)
- httpx (async HTTP client)
- SSE (Server-Sent Events for streaming)

**External Services:**
- Azure AD OAuth2 (authentication)
- AskAT&T API (OpenAI GPT-4o chat)
- AskDocs API (domain-specific RAG)

## Code Organization

### Backend Structure

```
backend/
├── app/
│   ├── api/v1/          # API route handlers
│   ├── services/        # Business logic & external APIs
│   │   ├── azure_ad.py       # Azure AD OAuth2
│   │   ├── askatt.py         # Real AskAT&T service
│   │   ├── askatt_mock.py    # Mock AskAT&T service
│   │   └── askdocs_mock.py   # Mock AskDocs service
│   ├── models/          # Database models
│   ├── schemas/         # Request/response schemas
│   └── core/            # Core utilities
├── alembic/             # Database migrations
├── scripts/             # Utility scripts
├── tests/               # Test suite
└── docs/                # (This documentation)
```

### Key Service Files

| File | Purpose | Dependencies |
|------|---------|--------------|
| `services/azure_ad.py` | Azure AD token management | httpx, settings |
| `services/askatt.py` | Real AskAT&T API integration | azure_ad, httpx |
| `services/askatt_mock.py` | Mock AskAT&T for development | None |
| `services/conversation.py` | Conversation management | database, models |

## Quick Reference

### Environment Setup

```bash
# 1. Copy environment template
cp backend/.env.example backend/.env

# 2. Edit .env with your settings
# For local dev: Keep USE_MOCK_ASKATT=true
# For production: Set USE_MOCK_ASKATT=false and configure Azure AD

# 3. Install dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Setup database
createdb askdocs_db
alembic upgrade head
python scripts/create_admin.py

# 5. Run server
uvicorn app.main:app --reload
```

### Common Commands

```bash
# Start backend
cd backend && uvicorn app.main:app --reload

# Run tests
cd backend && pytest

# Database migration
cd backend && alembic upgrade head

# Check .env protection
git check-ignore -v backend/.env

# Test Azure AD auth
cd backend && python -c "import asyncio; from app.services.azure_ad import get_askatt_token; asyncio.run(get_askatt_token())"
```

### Troubleshooting

| Issue | Solution | Documentation |
|-------|----------|---------------|
| Database connection error | Check DATABASE_URL in .env | [README.md](backend/README.md) |
| Azure AD auth failure | Check credentials, network access | [ASKATT_TESTING.md](backend/ASKATT_TESTING.md) |
| SSL verification error | Set verify=False for dev (enable in prod!) | [SECURITY.md](backend/SECURITY.md) |
| Server won't start | Check port 8000, review logs | [README.md](backend/README.md) |

## Getting Help

1. **Check documentation** - Start with [README.md](backend/README.md)
2. **Review API docs** - http://localhost:8000/docs
3. **Check logs** - Backend console output
4. **Security issues** - See [SECURITY.md](backend/SECURITY.md)
5. **Testing issues** - See [ASKATT_TESTING.md](backend/ASKATT_TESTING.md)

## Documentation Updates

Last updated: 2025-10-20

### Recent Changes

- ✅ Created comprehensive README.md
- ✅ Updated .env.example with all current settings
- ✅ Created SECURITY.md with security guidelines
- ✅ Created DOCUMENTATION_INDEX.md (this file)
- ✅ Created .gitignore to protect credentials
- ✅ Sanitized all documentation (removed real credentials)
- ✅ Verified .env protection in git
- ✅ Documented Azure AD scope requirement (/.default)
- ✅ Updated AskAT&T service for dual response format support (2025-10-20)
- ✅ Updated AskDocs service for citations parsing (2025-10-20)
- ✅ Updated ASKATT_INTEGRATION.md with dual format documentation (2025-10-20)
- ✅ Updated ASKDOCS_API_INTEGRATION.md with citations format (2025-10-20)

### Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| README.md | ✅ Complete | 2025-10-18 |
| ASKATT_INTEGRATION.md | ✅ Complete with Dual Format Support | 2025-10-20 |
| ASKATT_TESTING.md | ✅ Complete & Sanitized | 2025-10-18 |
| ASKDOCS_API_INTEGRATION.md | ✅ Complete with Citations Format | 2025-10-20 |
| MOCK_CONFIGURATION_GUIDE.md | ✅ Complete | Earlier |
| SECURITY.md | ✅ Complete | 2025-10-18 |
| .env.example | ✅ Updated | 2025-10-18 |
| .gitignore | ✅ Created | 2025-10-18 |
| CHANGELOG.md | ✅ Created | 2025-10-20 |
| zzz_issues.md | ✅ Updated (Fixed issues marked) | 2025-10-20 |
| DOCUMENTATION_INDEX.md | ✅ Complete | 2025-10-20 |

## Contributing

When updating documentation:

1. **Never commit real credentials** - Use placeholders in all docs
2. **Update DOCUMENTATION_INDEX.md** - When adding new docs
3. **Keep .env.example in sync** - When adding new env variables
4. **Update version history** - At the end of each document
5. **Test all examples** - Ensure code examples work
6. **Review SECURITY.md** - For security-related changes

---

**Project:** AI Chat Application
**Repository:** j_askdocs
**Backend Framework:** FastAPI
**Database:** PostgreSQL
**Authentication:** JWT + Azure AD OAuth2
