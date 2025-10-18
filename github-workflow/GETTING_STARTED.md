# Getting Started with GitHub Workflow

**Quick Start Guide**  
**For**: Managing j_askdocs application across Internal Server and External PC

---

## 🎯 Quick Overview

You're managing **two environments** of the same application:

| Environment | Purpose | Location | Push to GitHub? |
|-------------|---------|----------|-----------------|
| **External PC** | Development | Your personal Windows PC | ✅ Yes, freely |
| **Internal Server** | Testing/Production | Company server | ⚠️ No (pull only) |

**Key Principle**: Same code, different configuration files (.env)

---

## ⚡ 5-Minute Setup

### **1. Setup External PC** (Development Environment)

```powershell
# You're already here!
cd C:\Users\admin\Documents\AI_projects\j_askdocs

# Create .env file from template
cd backend
copy env.development.template .env

# That's it! The .env file has safe development settings

# Start developing
cd ..
# Backend: uvicorn app.main:app --reload (in one terminal)
# Frontend: cd frontend && npm run dev (in another terminal)
```

### **2. Setup Internal Server** (Production Environment)

```bash
# Clone the repository on internal server
git clone https://github.com/Martinb113/J_askattdocsUI.git
cd J_askattdocsUI

# Create .env with production settings
cd backend
cp env.production.template .env

# ⚠️ IMPORTANT: Edit .env with REAL company credentials
nano .env
# or: vim .env

# Set strict permissions (Linux)
chmod 600 .env

# Start the application
# ... start backend and frontend ...
```

---

## 📖 Documentation Guide

### **Start Here** (You are here! 📍)

1. **[README.md](README.md)** - Documentation index (overview of all files)

### **For Daily Development**

2. **[WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)** - Your main reference
   - Daily workflows for External PC
   - How to sync with Internal Server
   - Common commands and patterns
   - **Read this first!**

3. **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Configuration guide
   - Setting up .env files
   - Environment variables reference
   - Troubleshooting configuration issues

### **For Security**

4. **[SAFETY_CHECKLIST.md](SAFETY_CHECKLIST.md)** - Safety procedures
   - What to check before pushing
   - How to avoid committing sensitive data
   - Emergency procedures if you make a mistake

5. **[PRE_COMMIT_HOOKS.md](PRE_COMMIT_HOOKS.md)** - Automated protection
   - Setting up pre-commit hooks
   - Automatically block sensitive data
   - Testing and troubleshooting hooks

### **For Future** (Not active yet)

6. **[PRODUCTION_WORKFLOW.md](PRODUCTION_WORKFLOW.md)** - Advanced workflow
   - Issue-driven development
   - For when you have real users
   - Structured bug reporting and fixing
   - **Don't use this yet - it's for later!**

---

## 🚀 Common Daily Tasks

### **Task 1: Start Your Development Day**

```powershell
# On External PC
cd C:\Users\admin\Documents\AI_projects\j_askdocs

# Pull any updates
git pull origin main

# Start working
# ... make changes ...

# When done for the day
git add .
git commit -m "Feature: What you did today"
git push origin main
```

### **Task 2: Update Internal Server with Your Changes**

```bash
# On Internal Server
cd /path/to/j_askdocs

# Pull latest changes
git pull origin main

# Restart services
# ... restart backend/frontend ...

# Test with production data
# ... manual testing ...
```

### **Task 3: Fix a Bug Found on Internal Server**

```powershell
# On External PC (safer to develop here)

# 1. Note what the bug is
# (Mental note or create a quick text file locally)

# 2. Try to reproduce locally
# ... test with development environment ...

# 3. Fix the code
# ... edit files ...

# 4. Test the fix
# ... verify it works ...

# 5. Commit and push
git add .
git commit -m "Fix: Description of what was broken and how you fixed it"
git push origin main

# 6. Update Internal Server
# (On Internal: git pull origin main)
```

---

## 🔒 Safety Rules (CRITICAL!)

### **The Golden Rules**

1. **NEVER commit .env files** ❌
   - They contain sensitive credentials
   - Use env.development.template and env.production.template instead

2. **Work on External PC for code changes** ✅
   - Safer environment
   - No risk of committing sensitive data
   - Better development tools

3. **Internal Server pulls only** ✅
   - Don't push code from Internal Server
   - Only pull changes from GitHub
   - Exception: Can push issue documentation (in future production workflow)

4. **Review before push** ✅
   - Always run `git status` and `git diff`
   - Make sure you're not committing anything sensitive
   - External PC: Quick review
   - Internal Server: VERY thorough review (if you must push)

5. **Keep .env files separate** ✅
   - External PC: Development settings (mock services)
   - Internal Server: Production settings (real credentials)
   - Never mix them up!

---

## 🐛 Troubleshooting

### **Problem: "Can't find .env file" or "Configuration error"**

**Solution:**
```powershell
# Create .env from template
cd backend
copy env.development.template .env

# Verify it exists
dir .env
```

### **Problem: "Git won't let me commit"**

**Solution:**
```powershell
# Check what's wrong
git status

# If pre-commit hook is blocking, review the changes
git diff

# Make sure you're not committing sensitive data
# See SAFETY_CHECKLIST.md for detailed review
```

### **Problem: "Changes on Internal not showing on External"**

**Solution:**
```powershell
# On External PC, pull the changes
git pull origin main

# If there are no changes, Internal Server probably didn't push
# That's correct! Internal Server should only pull, not push
```

### **Problem: "Merge conflict"**

**Solution:**
```powershell
# See what's conflicting
git status

# If it's .env file - that shouldn't happen (it's ignored)
# If it's code, edit the file and resolve:
# Look for <<<<<<< and >>>>>>>
# Keep the version you want
# Remove the conflict markers

git add <resolved-file>
git commit -m "Resolved merge conflict"
```

### **Problem: "Accidentally committed sensitive data"**

**Solution:**
- **Stop immediately!**
- **Don't push if you haven't yet!**
- See [SAFETY_CHECKLIST.md](SAFETY_CHECKLIST.md) "Emergency" section
- Follow the detailed recovery steps

---

## 📝 Quick Command Reference

### **Daily Commands (External PC)**

```powershell
# Check status
git status

# Pull latest
git pull origin main

# Review changes
git diff

# Commit changes
git add .
git commit -m "Type: Description"

# Push to GitHub
git push origin main
```

### **Daily Commands (Internal Server)**

```bash
# Pull latest code
git pull origin main

# Check .env is still there
ls -la .env

# That's it! Don't push from here.
```

### **Safety Commands**

```powershell
# Check if .env is ignored
git check-ignore backend/.env
# Should output: backend/.env

# See what would be committed
git status
git diff --staged

# Undo last commit (before push)
git reset --soft HEAD~1
```

---

## ✅ Setup Verification Checklist

### **External PC Setup**
- [ ] Repository cloned to `C:\Users\admin\Documents\AI_projects\j_askdocs`
- [ ] Created `backend/.env` from `env.development.template`
- [ ] `.env` file is in `.gitignore` (verify with `git check-ignore backend/.env`)
- [ ] Can start backend: `uvicorn app.main:app --reload`
- [ ] Can start frontend: `cd frontend && npm run dev`
- [ ] Application loads at `http://localhost:5173`
- [ ] Can push to GitHub without errors: `git push origin main`

### **Internal Server Setup**
- [ ] Repository cloned on company internal server
- [ ] Created `backend/.env` from `env.production.template`
- [ ] Edited `.env` with REAL company credentials
- [ ] Set file permissions: `chmod 600 backend/.env` (Linux)
- [ ] `.env` file is in `.gitignore` (verify with `git check-ignore backend/.env`)
- [ ] Can start application with production config
- [ ] Real Azure AD authentication works
- [ ] Database connection works
- [ ] **Not pushing** to GitHub from internal server

### **Security Verification**
- [ ] Verified `.env` is in `.gitignore` (both environments)
- [ ] Confirmed `.env` doesn't show in `git status`
- [ ] Different `JWT_SECRET` in each environment
- [ ] Production `.env` has strong passwords
- [ ] Read and understood SAFETY_CHECKLIST.md
- [ ] Know what NOT to commit (credentials, .env, .db files)
- [ ] Know emergency procedures if sensitive data committed

---

## 🎓 Learning Path

**Day 1: Setup and Understanding**
- [ ] Read this guide (GETTING_STARTED.md)
- [ ] Setup External PC environment
- [ ] Read WORKFLOW_GUIDE.md
- [ ] Practice: Make a small change, commit, push

**Day 2: Configuration**
- [ ] Read ENVIRONMENT_SETUP.md
- [ ] Understand how .env files work
- [ ] Customize your development .env if needed
- [ ] Setup Internal Server environment

**Day 3: Security**
- [ ] Read SAFETY_CHECKLIST.md
- [ ] Read PRE_COMMIT_HOOKS.md
- [ ] (Optional) Setup pre-commit hooks
- [ ] Practice: Review git diff before committing

**Week 2+: Daily Workflow**
- [ ] Use WORKFLOW_GUIDE.md as reference
- [ ] Develop on External PC
- [ ] Test on Internal Server
- [ ] Build confidence with the workflow

**When Ready for Production:**
- [ ] Read PRODUCTION_WORKFLOW.md
- [ ] Implement issue-driven workflow
- [ ] Set up issue folder structure
- [ ] Start tracking issues systematically

---

## 💡 Pro Tips

1. **Commit Often**
   - Small, logical commits are better than large ones
   - Easy to review, easy to revert if needed
   - Descriptive commit messages help future you

2. **Test Before Pushing**
   - Quick test on External PC
   - Catch obvious issues early
   - Internal Server testing is for integration with real services

3. **Use Descriptive Messages**
   - Good: "Fix: Azure AD token validation for production environment"
   - Bad: "fix", "update", "test"

4. **Keep Workflow Simple**
   - Don't overcomplicate with branches (for now)
   - Same code everywhere, different configuration
   - Only use branches if truly needed

5. **Document Decisions**
   - If you make a configuration change, note why
   - If you encounter a weird bug, document the solution
   - Future you will thank present you

---

## 🆘 Need Help?

### **Quick Questions**

| Question | See Document |
|----------|-------------|
| How do I commit and push? | [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) |
| What's in my .env file? | [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) |
| Is this safe to commit? | [SAFETY_CHECKLIST.md](SAFETY_CHECKLIST.md) |
| How do I set up hooks? | [PRE_COMMIT_HOOKS.md](PRE_COMMIT_HOOKS.md) |
| Planning for production? | [PRODUCTION_WORKFLOW.md](PRODUCTION_WORKFLOW.md) |

### **Common Workflows**

| I want to... | Steps |
|--------------|-------|
| Start my day | `git pull origin main` → develop → commit → push |
| Update internal server | (Internal) `git pull origin main` |
| Fix a bug | External PC: fix → test → commit → push |
| Change configuration | Edit `.env` file (never commit it!) |
| Add a feature | External PC: develop → test → commit → push |
| Check if safe to push | `git status` + `git diff` + SAFETY_CHECKLIST.md |

---

## 🎉 You're Ready!

You now have everything you need to manage the j_askdocs application across both environments safely and efficiently.

**Your workflow in a nutshell:**
1. ✅ Develop on External PC (safe, can push freely)
2. ✅ Push to GitHub (only from External PC)
3. ✅ Pull on Internal Server (test with real data)
4. ✅ Keep .env files separate (never commit them)
5. ✅ Review before pushing (especially from Internal)

**Start developing and push fearlessly (from External PC)! 🚀**

---

**Questions?** Check the other documentation files in this folder for detailed guidance on specific topics.

**Remember:** When in doubt, work on External PC and review SAFETY_CHECKLIST.md before pushing anything from Internal Server.

