# AI Chat Application - Quick Start Guide

This guide will help you get the backend running locally on your personal PC **without needing access to the corporate intranet or real AskDocs/AskAT&T endpoints**.

## Prerequisites

- **Python 3.11+** installed
- **PostgreSQL 15+** installed and running
- **Git** (for version control)

## Step 1: Install PostgreSQL

### Windows:

1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer (PostgreSQL 15 or higher)
3. During installation:
   - Set postgres user password (remember this!)
   - Port: 5432 (default)
   - Install pgAdmin 4 (recommended for GUI management)

4. After installation, create the database:

```bash
# Open Command Prompt or PowerSQL shell
psql -U postgres

# In the PostgreSQL shell:
CREATE DATABASE ai_chat_db;
\q
```

### Mac/Linux:

```bash
# Mac (using Homebrew)
brew install postgresql@15
brew services start postgresql@15
createdb ai_chat_db

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb ai_chat_db
```

## Step 2: Backend Setup

### 1. Create and activate virtual environment:

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables:

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with your settings (use notepad, vim, or any text editor)
# Update these key values:
```

**Minimal `.env` configuration for local development:**

```env
# Database (update password if you set a different one)
DATABASE_URL=postgresql+asyncpg://postgres:your_postgres_password@localhost:5432/ai_chat_db

# JWT Secret (generate a secure random string)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8

# MOCK MODE - Use mock services for local development
USE_MOCK_AZURE_AD=true
USE_MOCK_ASKATT=true
USE_MOCK_ASKDOCS=true

# Azure AD (not needed when USE_MOCK_AZURE_AD=true, but keep placeholders)
AZURE_TENANT_ID=mock-tenant-id
AZURE_CLIENT_ID=mock-client-id
AZURE_CLIENT_SECRET=mock-client-secret

# API Endpoints (not needed in mock mode, but keep placeholders)
ASKATT_API_URL=http://mock-askatt-api
ASKDOCS_API_URL=http://mock-askdocs-api

# CORS (add your frontend URL if you build one)
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Debug
DEBUG=true
```

### 4. Run database migrations:

```bash
# Initialize Alembic (first time only)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Seed the database with initial data:

```bash
python scripts/seed_data.py
```

This will create:
- Default roles (USER, OIS, SIM, MANAGER, KNOWLEDGE_STEWARD, ADMIN)
- Sample domains (AT&T Support, Network Operations, Security Policies, HR Policies)
- Sample configurations with role assignments
- **Admin user** with credentials:
  - **AT&T ID**: `admin`
  - **Password**: `Admin123!`

### 6. Start the development server:

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python -m app.main
```

The backend will be running at:
- **API**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Step 3: Test the API

### 1. Health Check:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Chat Application API",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Login as Admin:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"attid": "admin", "password": "Admin123!"}'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "attid": "admin",
    "email": "admin@att.com",
    "full_name": "Admin User",
    "is_active": true,
    "roles": ["ADMIN"]
  }
}
```

**Copy the `access_token` value - you'll need it for subsequent requests!**

### 3. Test AskAT&T Chat (MOCK):

```bash
# Replace <YOUR_TOKEN> with the access token from step 2
curl -X POST http://localhost:8000/api/v1/chat/askatt \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}' \
  --no-buffer
```

You should see token-by-token streaming response like:
```
data: {"type":"conversation_id","conversation_id":"..."}

data: {"type":"token","content":"H"}

data: {"type":"token","content":"e"}

data: {"type":"token","content":"l"}
...
data: {"type":"usage","usage":{"prompt_tokens":3,"completion_tokens":25,"total_tokens":28}}

data: {"type":"end"}
```

### 4. List Available Configurations:

```bash
curl -X GET http://localhost:8000/api/v1/chat/configurations \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

### 5. Test AskDocs Chat (MOCK RAG):

```bash
# Get a configuration_id from step 4, then:
curl -X POST http://localhost:8000/api/v1/chat/askdocs \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I reset my password?", "configuration_id": "<CONFIG_ID>"}' \
  --no-buffer
```

You should see streaming response with **sources**:
```
data: {"type":"token","content":"T"}
...
data: {"type":"sources","sources":[{"title":"AT&T Password Reset Guide","url":"https://att.com/support/password-reset"}]}

data: {"type":"usage","usage":{...}}

data: {"type":"end"}
```

## Step 4: Explore the API

Open http://localhost:8000/docs in your browser to see the **interactive API documentation** (Swagger UI).

You can:
1. Click "Authorize" button and enter: `Bearer <YOUR_TOKEN>`
2. Test all endpoints interactively
3. See request/response schemas
4. Copy curl commands

## Common Operations

### Create a New User:

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "attid": "jsmith",
    "email": "jsmith@att.com",
    "password": "SecurePass123!",
    "full_name": "John Smith"
  }'
```

### Assign Roles to User (Admin only):

```bash
# Get user ID and role IDs first, then:
curl -X POST http://localhost:8000/api/v1/admin/users/<USER_ID>/roles \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<USER_ID>",
    "role_ids": ["<ROLE_ID_1>", "<ROLE_ID_2>"]
  }'
```

### List Conversations:

```bash
curl -X GET http://localhost:8000/api/v1/chat/conversations \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

### Submit Feedback on a Message:

```bash
curl -X POST http://localhost:8000/api/v1/chat/messages/<MESSAGE_ID>/feedback \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"rating": 5, "comment": "Very helpful!"}'
```

## Troubleshooting

### Database Connection Error:

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Ensure PostgreSQL is running and DATABASE_URL in `.env` is correct.

```bash
# Windows
# Check if postgres service is running in Services app

# Mac
brew services list

# Linux
sudo systemctl status postgresql
```

### Import Errors:

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**: Ensure virtual environment is activated and dependencies are installed.

```bash
# Activate venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### JWT Token Expired:

```
401 Unauthorized: Token validation failed
```

**Solution**: Login again to get a new token (tokens expire after 8 hours by default).

### Role-Based Access Issues:

```
403 Forbidden: Configuration not found or access denied
```

**Solution**:
1. Check user has the correct role assigned
2. Verify configuration has that role in its access list
3. Use admin endpoints to assign roles

## MOCK Services Explained

Since you're developing on a personal PC, the application uses **MOCK services** that simulate the real AskAT&T and AskDocs APIs:

- **`askatt_mock.py`**: Simulates OpenAI chat responses with token-by-token streaming
- **`askdocs_mock.py`**: Simulates RAG chat with source attribution based on keywords
- **`azure_ad_mock.py`**: Simulates Azure AD token generation

These mocks allow you to:
- ✅ Develop and test the full application flow
- ✅ Test role-based access control
- ✅ Test streaming responses
- ✅ Test conversation persistence
- ✅ Test feedback collection

**When deploying to production**, you'll:
1. Set `USE_MOCK_*=false` in `.env`
2. Provide real Azure AD credentials
3. Update `ASKATT_API_URL` and `ASKDOCS_API_URL` to real endpoints
4. Replace mock service imports with real implementations

## Next Steps

1. **Build Frontend**: Create a React/Vue/Angular frontend to consume this API
2. **Test All Endpoints**: Use the `/docs` page to test every endpoint
3. **Customize Roles**: Add new roles and configurations based on your needs
4. **Add Real Services**: When you have access to intranet, replace mocks with real APIs

## Production Checklist

Before deploying to production:

- [ ] Change JWT_SECRET to a secure random string
- [ ] Change default admin password
- [ ] Set DEBUG=false
- [ ] Use real Azure AD credentials
- [ ] Configure real API endpoints
- [ ] Set up proper CORS origins
- [ ] Use environment-specific configuration
- [ ] Set up proper logging and monitoring
- [ ] Run database migrations (not create_all)
- [ ] Set up database backups
- [ ] Configure HTTPS/TLS
- [ ] Review and harden security settings

## Support

For questions or issues:
1. Check the `/docs` endpoint for API documentation
2. Review logs in the console
3. Check `IMPLEMENTATION_STATUS.md` for feature status
4. Review the codebase for detailed comments

Happy coding! 🚀
