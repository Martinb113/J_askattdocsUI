# AI Chat Application - Backend

FastAPI-based backend for the AI Chat Application with dual AI chat services: **AskAT&T** (general OpenAI chat) and **AskDocs** (domain-specific RAG chat).

## Features

- **Dual AI Chat Services**
  - **AskAT&T**: General-purpose OpenAI GPT-4o chat with Azure AD OAuth2 authentication
  - **AskDocs**: Domain-specific RAG (Retrieval-Augmented Generation) chat with role-based access control

- **Authentication & Authorization**
  - JWT-based user authentication
  - Role-based access control (Admin, PowerUser, User)
  - Azure AD OAuth2 integration for AskAT&T API

- **Real-time Streaming**
  - Server-Sent Events (SSE) for token-by-token AI responses
  - Conversation history management
  - Message feedback system

- **Mock Services**
  - Complete mock implementations for local development
  - No network dependencies when using mock mode
  - Realistic mock data for testing

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Access to Azure AD (for AskAT&T production mode)
- Access to internal API gateway (for production mode)

### Installation

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   # Copy example configuration
   cp .env.example .env

   # Edit .env with your settings
   # For local development, keep USE_MOCK_ASKATT=true
   # For production, set USE_MOCK_ASKATT=false and configure Azure AD
   ```

5. **Initialize database:**
   ```bash
   # Start PostgreSQL and create database
   createdb askdocs_db

   # Run migrations
   alembic upgrade head

   # Create admin user (username: admin, password: Admin123!)
   python scripts/create_admin.py
   ```

6. **Run the server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Configuration

### Environment Variables

The application uses `.env` file for configuration. See `.env.example` for all available options.

**Critical Settings:**

```bash
# Mock Mode (for local development)
USE_MOCK_ASKATT=true    # Use mock AskAT&T service
USE_MOCK_ASKDOCS=true   # Use mock AskDocs service
USE_MOCK_AZURE_AD=true  # Skip Azure AD authentication

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/askdocs_db

# JWT Authentication
JWT_SECRET=your-secure-random-secret-here
JWT_EXPIRATION_HOURS=8
```

**Azure AD Configuration (for AskAT&T production mode):**

```bash
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_AUTH_URL=https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token
AZURE_SCOPE_ASKATT_GENERAL=api://{api-id}/.default
AZURE_SCOPE_ASKATT_DOMAIN=api://{api-id}/.default
```

**IMPORTANT:** Client credential flows require `/.default` suffix for scopes. See [ASKATT_INTEGRATION.md](./ASKATT_INTEGRATION.md) for details.

**AskAT&T API Configuration:**

```bash
ASKATT_API_BASE_URL_STAGE=https://your-gateway/stage/domain-services/chat-generativeai
ASKATT_API_BASE_URL_PRODUCTION=https://your-gateway/prod/domain-services/chat-generativeai
ASKATT_DOMAIN_NAME=GenerativeAI
ASKATT_MODEL_NAME=gpt-4o
ASKATT_MAX_TOKENS=800
```

### Mock vs. Production Mode

The application supports two modes for external services:

#### Mock Mode (Default for Local Development)

**Configuration:**
```bash
USE_MOCK_ASKATT=true
USE_MOCK_ASKDOCS=true
```

**Benefits:**
- No network dependencies
- No Azure AD authentication required
- Instant responses for rapid development
- Realistic mock data

**Use Cases:**
- Local development
- Frontend UI testing
- CI/CD testing without external dependencies

#### Production Mode

**Configuration:**
```bash
USE_MOCK_ASKATT=false
USE_MOCK_ASKDOCS=false
```

**Requirements:**
- Network access to Azure AD
- Network access to AskAT&T/AskDocs API endpoints
- Valid Azure AD credentials
- API gateway access

**Use Cases:**
- Integration testing
- Staging environment
- Production deployment

### Mock Data Configuration

The application includes realistic mock data for development:

**SD_International Domain Configurations:**
- `sim_wiki_con_v1v1` - SIM Wiki Configuration v1.1
- `ois_wiki_com_v1v1` - OIS Wiki Configuration v1.1

See [MOCK_CONFIGURATION_GUIDE.md](./MOCK_CONFIGURATION_GUIDE.md) for details.

## Documentation

### API Integration Guides

- **[ASKATT_INTEGRATION.md](./ASKATT_INTEGRATION.md)** - Complete guide to AskAT&T API integration with Azure AD OAuth2
- **[ASKATT_TESTING.md](./ASKATT_TESTING.md)** - Comprehensive testing guide with test results and procedures
- **[MOCK_CONFIGURATION_GUIDE.md](./MOCK_CONFIGURATION_GUIDE.md)** - Guide to mock configuration system for AskDocs

### API Endpoints

#### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

#### Chat Services

- `POST /api/v1/chat/askatt` - Chat with AskAT&T (general OpenAI chat)
- `POST /api/v1/chat/askdocs` - Chat with AskDocs (domain-specific RAG chat)
- `GET /api/v1/chat/conversations` - List user conversations
- `GET /api/v1/chat/conversations/{id}` - Get conversation details
- `DELETE /api/v1/chat/conversations/{id}` - Delete conversation

#### Configuration

- `GET /api/v1/chat/configurations` - List AskDocs configurations (role-based)
- `POST /api/v1/chat/messages/{id}/feedback` - Submit message feedback

See API documentation at http://localhost:8000/docs for full details.

## Architecture

### Technology Stack

- **Framework:** FastAPI (async)
- **Database:** PostgreSQL with AsyncPG
- **ORM:** SQLAlchemy 2.0 (async)
- **Authentication:** JWT tokens
- **Streaming:** Server-Sent Events (SSE)
- **HTTP Client:** httpx (async)

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │ AskAT&T Chat │      │ AskDocs Chat │                     │
│  └──────┬───────┘      └──────┬───────┘                     │
│         │                     │                              │
│         │ Mock Mode          │ Mock Mode                    │
│         ▼                     ▼                              │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │ Mock Service │      │ Mock Service │                     │
│  └──────────────┘      └──────────────┘                     │
│         │                     │                              │
│         │ Production Mode    │ Production Mode              │
│         ▼                     ▼                              │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │ Azure AD     │      │ AskDocs API  │                     │
│  │ + AskAT&T API│      │              │                     │
│  └──────────────┘      └──────────────┘                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **`app/api/v1/`** - API route handlers
- **`app/services/`** - Business logic and external API integrations
  - `azure_ad.py` - Azure AD OAuth2 authentication
  - `askatt.py` - Real AskAT&T API service
  - `askatt_mock.py` - Mock AskAT&T service
  - `askdocs_mock.py` - Mock AskDocs service
  - `conversation.py` - Conversation management
- **`app/models/`** - SQLAlchemy database models
- **`app/schemas/`** - Pydantic request/response schemas
- **`app/core/`** - Core utilities (auth, exceptions, security)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/

# Linting
ruff check app/
```

## Testing AskAT&T Integration

### Quick Test (Mock Mode)

```bash
# 1. Ensure mock mode is enabled
echo "USE_MOCK_ASKATT=true" >> .env

# 2. Start server
uvicorn app.main:app --reload

# 3. Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123!"}'

# 4. Test chat (replace YOUR_TOKEN)
curl -X POST http://localhost:8000/api/v1/chat/askatt \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' \
  --no-buffer
```

### Production Test (Real API)

See [ASKATT_TESTING.md](./ASKATT_TESTING.md) for complete testing procedures.

## Security Considerations

### Before Production Deployment

- [ ] Change all default passwords
- [ ] Use strong JWT_SECRET (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] Enable SSL certificate verification in Azure AD and API clients (change `verify=False` to `verify=True`)
- [ ] Review CORS settings - restrict to production domains only
- [ ] Ensure `.env` file is not committed to version control (already in `.gitignore`)
- [ ] Use environment-specific secrets management (Azure Key Vault, AWS Secrets Manager, etc.)
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper logging (remove debug logs of sensitive data)
- [ ] Set up rate limiting for API endpoints
- [ ] Review and restrict database user permissions

### Credential Management

**NEVER commit credentials to version control:**
- `.env` file is in `.gitignore`
- Use `.env.example` as template with placeholder values
- Store production secrets in secure secrets management system

**Documentation has been sanitized:**
- `ASKATT_INTEGRATION.md` uses placeholder values
- `ASKATT_TESTING.md` uses placeholder values
- `.env.example` uses placeholder values
- Actual `.env` file contains real credentials (not committed)

## Troubleshooting

### Common Issues

**Database Connection Error:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify DATABASE_URL in .env
# Ensure database exists: createdb askdocs_db
```

**Azure AD Authentication Error:**
```bash
# Check credentials in .env
# Verify network access to login.microsoftonline.com
# Ensure scope uses /.default suffix
# See ASKATT_INTEGRATION.md for details
```

**Server Won't Start:**
```bash
# Check port 8000 is available
lsof -i :8000  # On Linux/Mac
netstat -ano | findstr :8000  # On Windows

# Check logs for specific error
# Verify all dependencies installed: pip install -r requirements.txt
```

For more troubleshooting help, see:
- [ASKATT_TESTING.md](./ASKATT_TESTING.md) - Authentication and API troubleshooting
- API logs in console output
- `/docs` endpoint for API documentation

## Support

For issues or questions:
1. Check the documentation in this directory
2. Review API documentation at `/docs`
3. Check backend console logs for error details
4. Review Azure AD portal for authentication issues
5. Contact API team for endpoint access issues

## License

Internal use only - proprietary software.
