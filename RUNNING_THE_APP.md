# 🚀 Running the Application

## Quick Start (Easiest Way)

### Option 1: Automatic Setup (Windows)

**Double-click** `setup_and_run.bat` in the project root.

This script will:
1. ✅ Check all prerequisites (Python, Node, PostgreSQL)
2. ✅ Create virtual environment
3. ✅ Install all dependencies
4. ✅ Create database
5. ✅ Run migrations
6. ✅ Seed initial data
7. ✅ Start both backend and frontend

**That's it!** Two windows will open automatically.

---

### Option 2: Manual Startup (After Initial Setup)

Once you've run the setup script once, you can start the servers individually:

**Start Backend**:
- Double-click `start_backend.bat`
- Or run in terminal:
  ```bash
  cd backend
  venv\Scripts\activate
  uvicorn app.main:app --reload
  ```

**Start Frontend**:
- Double-click `start_frontend.bat`
- Or run in terminal:
  ```bash
  cd frontend
  npm run dev
  ```

---

## Access the Application

Once both servers are running:

### Frontend
- **URL**: http://localhost:3000
- **Login**:
  - AT&T ID: `admin`
  - Password: `Admin123!`

### Backend API
- **URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## First Time Setup (Manual Steps)

If the automatic script doesn't work, follow these steps:

### 1. Install Prerequisites

**PostgreSQL**:
1. Download: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember your postgres password!
4. Add to PATH: `C:\Program Files\PostgreSQL\15\bin`

**Python 3.11+**:
1. Download: https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation

**Node.js 18+**:
1. Download: https://nodejs.org/
2. Install LTS version

### 2. Create Database

```bash
# Open Command Prompt
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE ai_chat_db;
\q
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env
copy .env.example .env
notepad .env  # Edit DATABASE_URL with your postgres password

# Run migrations
alembic revision --autogenerate -m "Initial"
alembic upgrade head

# Seed data
python scripts\seed_data.py

# Start server
uvicorn app.main:app --reload
```

### 4. Setup Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Create .env (optional, defaults are fine)
copy .env.example .env

# Start server
npm run dev
```

---

## Testing the Application

### 1. Login
- Go to http://localhost:3000
- Login with `admin` / `Admin123!`

### 2. Test AskAT&T
- Default tab should be selected
- Type: "Hello, how are you?"
- Press Enter
- Watch token-by-token streaming!

### 3. Test AskDocs
- Click "AskDocs" tab
- Select a configuration from dropdown
- Type: "How do I reset my password?"
- See sources at the bottom with clickable links!

### 4. Create New User
- Logout (top right)
- Click "Sign up"
- Fill the form (password must have uppercase, lowercase, number)
- Auto-login after signup!

### 5. Test Feedback
- Send a message
- Click thumbs up or thumbs down
- Feedback is saved to database!

---

## Stopping the Application

**To stop gracefully**:
- Press `Ctrl+C` in the backend terminal
- Press `Ctrl+C` in the frontend terminal

**To force stop**:
```bash
# Kill backend (port 8000)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill frontend (port 3000)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

## Common Commands

### Backend:

```bash
# Start development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View database
psql -U postgres -d ai_chat_db
```

### Frontend:

```bash
# Start development server
npm run dev

# Start on different port
npm run dev -- --port 3001

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type check
npm run type-check
```

---

## Environment Configuration

### Backend `.env`:
```env
# Required
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/ai_chat_db
JWT_SECRET=your-super-secret-jwt-key

# MOCK Services (true for local dev)
USE_MOCK_ASKATT=true
USE_MOCK_ASKDOCS=true
USE_MOCK_AZURE_AD=true

# Only needed if MOCK services are false
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
ASKATT_API_URL=https://your-api.com
ASKDOCS_API_URL=https://your-api.com

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend `.env`:
```env
# Backend API URL
VITE_API_URL=http://localhost:8000
```

---

## Troubleshooting

### "Cannot connect to database"

**Check PostgreSQL is running**:
```bash
# Windows Services
services.msc
# Find: postgresql-x64-15
# Status should be "Running"
```

**Test connection**:
```bash
psql -U postgres -d ai_chat_db -c "SELECT 1;"
```

**Fix DATABASE_URL** in `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/ai_chat_db
```

### "Module not found" (Backend)

```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### "Module not found" (Frontend)

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### "Port already in use"

**Backend (8000)**:
```bash
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

**Frontend (3000)**:
```bash
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F
# Or start on different port:
npm run dev -- --port 3001
```

### "Alembic error"

**Reset database**:
```bash
psql -U postgres
DROP DATABASE ai_chat_db;
CREATE DATABASE ai_chat_db;
\q

cd backend
alembic upgrade head
python scripts\seed_data.py
```

### "CORS error" in browser

Check backend `.env`:
```env
CORS_ORIGINS=["http://localhost:3000"]
```

Restart backend after changes.

---

## Development Tips

### Hot Reload

Both servers support hot reload:
- **Backend**: Auto-reloads on `.py` file changes
- **Frontend**: Auto-reloads on `.tsx`, `.ts`, `.css` changes

### Browser DevTools

Press `F12` to open:
- **Console**: See errors and logs
- **Network**: See API calls and SSE streams
- **Application**: Check localStorage for tokens

### Database GUI

**pgAdmin 4** (included with PostgreSQL):
- Open pgAdmin
- Connect to postgres
- Navigate to: Servers → PostgreSQL 15 → Databases → ai_chat_db
- View tables, run queries

### API Testing

**Use the interactive docs**:
1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Login to get token
4. Paste token: `Bearer <your_token>`
5. Test all endpoints interactively!

---

## Next Steps

Once the app is running:

1. **Explore Features**:
   - Try both chat services
   - Create multiple users
   - Test role-based access
   - Rate messages

2. **Customize**:
   - Modify UI colors in `frontend/tailwind.config.js`
   - Add new roles in database
   - Create new configurations

3. **Deploy**:
   - See `DEPLOYMENT.md` for server deployment
   - Use Docker: `docker-compose up -d`

4. **Replace MOCKs**:
   - When you have intranet access
   - Set `USE_MOCK_*=false`
   - Configure real API endpoints

---

## Quick Reference

### URLs:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Credentials:
- AT&T ID: `admin`
- Password: `Admin123!`

### Scripts:
- **Full Setup**: `setup_and_run.bat`
- **Backend Only**: `start_backend.bat`
- **Frontend Only**: `start_frontend.bat`

---

**🎉 You're all set! Enjoy the application!**

For more details:
- **Setup Guide**: `START_HERE.md`
- **Backend Guide**: `backend/QUICKSTART.md`
- **Frontend Guide**: `frontend/SETUP.md`
- **Deployment**: `DEPLOYMENT.md`
