# 🚀 Quick Start Guide - Run the Application

This guide will help you run the AI Chat Application on your Windows PC in just a few steps.

---

## ✅ Prerequisites Check

Before starting, ensure you have:

- [ ] **Python 3.11+** - [Download](https://www.python.org/downloads/)
- [ ] **Node.js 18+** - [Download](https://nodejs.org/)
- [ ] **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/windows/)

### Quick Check:

```bash
python --version    # Should show Python 3.11.x or higher
node --version      # Should show v18.x.x or higher
psql --version      # Should show psql 15.x or higher
```

---

## 📥 Step 1: Install PostgreSQL (If Not Installed)

### Windows Installation:

1. **Download**: https://www.postgresql.org/download/windows/
2. **Run installer**: `postgresql-15.x-windows-x64.exe`
3. **During installation**:
   - Port: `5432` (default)
   - Password: Choose a password (remember this!)
   - Install pgAdmin 4 (recommended)

4. **After installation**, add PostgreSQL to PATH:
   - Search for "Environment Variables" in Windows
   - Edit System Variables → PATH
   - Add: `C:\Program Files\PostgreSQL\15\bin`

5. **Restart your terminal** for PATH changes to take effect

---

## 🗄️ Step 2: Create Database

Open **Command Prompt** or **PowerShell** as Administrator:

```bash
# Option 1: Using psql command
psql -U postgres

# In the PostgreSQL prompt:
CREATE DATABASE ai_chat_db;
\q

# Option 2: Using pgAdmin
# Open pgAdmin → Right-click Databases → Create → Database
# Name: ai_chat_db
```

---

## ⚙️ Step 3: Setup Backend

Open a **new terminal window**:

```bash
# Navigate to backend folder
cd C:\Users\admin\Documents\AI_projects\j_askdocs\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env file with Notepad
notepad .env
```

**Edit these lines in `.env`**:
```env
# Update with YOUR PostgreSQL password
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD_HERE@localhost:5432/ai_chat_db

# Generate a secure JWT secret or use this example
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Keep these as true for local development
USE_MOCK_ASKATT=true
USE_MOCK_ASKDOCS=true
USE_MOCK_AZURE_AD=true
```

Save and close the file.

**Run migrations and seed data**:

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Seed database (creates admin user and sample data)
python scripts\seed_data.py

# Start backend server
uvicorn app.main:app --reload
```

**✅ Backend is running!**
- URL: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Keep this terminal open!**

---

## 🎨 Step 4: Setup Frontend

Open a **second terminal window**:

```bash
# Navigate to frontend folder
cd C:\Users\admin\Documents\AI_projects\j_askdocs\frontend

# Install dependencies
npm install

# Create .env file
copy .env.example .env

# The default .env should work (no edits needed)
# But you can check:
notepad .env
```

**Start frontend**:

```bash
npm run dev
```

**✅ Frontend is running!**
- URL: http://localhost:3000

---

## 🎉 Step 5: Test the Application

1. **Open your browser**: http://localhost:3000

2. **Login with demo credentials**:
   - **AT&T ID**: `admin`
   - **Password**: `Admin123!`

3. **Test AskAT&T**:
   - Type: "Hello, how are you?"
   - Press Enter or click Send
   - Watch the **token-by-token streaming**!

4. **Test AskDocs**:
   - Click the "AskDocs" tab
   - Select a configuration from dropdown
   - Type: "How do I reset my password?"
   - See the **sources** at the bottom!

5. **Create a new user**:
   - Logout (top right)
   - Click "Sign up"
   - Fill in the form
   - You'll be auto-logged in!

---

## 🛑 Stopping the Application

**To stop**:
- Press `Ctrl+C` in both terminal windows
- Backend terminal: `Ctrl+C`
- Frontend terminal: `Ctrl+C`

**To start again**:
```bash
# Terminal 1 (Backend)
cd C:\Users\admin\Documents\AI_projects\j_askdocs\backend
venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2 (Frontend)
cd C:\Users\admin\Documents\AI_projects\j_askdocs\frontend
npm run dev
```

---

## 🐛 Troubleshooting

### Problem: "psql: command not found"
**Solution**: PostgreSQL not in PATH. Restart terminal after installation.

### Problem: "Cannot connect to database"
**Solution**:
1. Check PostgreSQL is running: Open Services → Find "postgresql-x64-15" → Start
2. Verify DATABASE_URL in `.env` has correct password
3. Test: `psql -U postgres -d ai_chat_db -c "SELECT 1;"`

### Problem: "Port 8000 already in use"
**Solution**: Another process using port 8000
```bash
# Find process
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID_NUMBER> /F
```

### Problem: "Port 3000 already in use"
**Solution**: Start frontend on different port
```bash
npm run dev -- --port 3001
# Then visit: http://localhost:3001
```

### Problem: "Module not found" errors
**Solution**: Reinstall dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Problem: "Alembic migration error"
**Solution**: Drop and recreate database
```bash
psql -U postgres
DROP DATABASE ai_chat_db;
CREATE DATABASE ai_chat_db;
\q

# Then run migrations again
alembic upgrade head
python scripts\seed_data.py
```

---

## 📝 Quick Reference

### Backend Commands:
```bash
# Start backend
uvicorn app.main:app --reload

# Run tests
pytest

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Seed database
python scripts\seed_data.py
```

### Frontend Commands:
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## 🎯 What's Next?

Now that the application is running:

1. **Explore Features**:
   - Try both AskAT&T and AskDocs
   - Create conversations
   - Rate messages (thumbs up/down)
   - Create multiple users

2. **Customize**:
   - Modify colors in `frontend/tailwind.config.js`
   - Add new roles in admin panel
   - Create new configurations

3. **Deploy**:
   - See `DEPLOYMENT.md` for server deployment
   - Use Docker: `docker-compose up -d`

4. **Replace MOCK Services**:
   - When you have intranet access
   - Set `USE_MOCK_*=false` in `.env`
   - Configure real API endpoints

---

## 📞 Need Help?

- **Backend issues**: Check `backend/QUICKSTART.md`
- **Frontend issues**: Check `frontend/SETUP.md`
- **Deployment**: Check `DEPLOYMENT.md`
- **Testing**: Check `TESTING_DEPLOYMENT_STATUS.md`
- **Overview**: Check `FULL_PROJECT_SUMMARY.md`

---

**🎉 Enjoy your AI Chat Application!**

**Default Admin Credentials**:
- AT&T ID: `admin`
- Password: `Admin123!`

**⚠️ Remember to change the admin password in production!**
