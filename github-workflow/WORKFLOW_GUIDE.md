# Development Workflow Guide

**Strategy**: Configuration-First + Protected Internal  
**Phase**: Development (Pre-Production)

---

## 🎯 Core Principles

1. **Same Code, Different Config**: Both environments use the same `main` branch
2. **Configuration-Driven**: All differences handled via `.env` files
3. **External Development**: Primary development happens on External PC
4. **Internal Testing**: Internal server tests with real company resources
5. **One-Way Sync**: Changes flow External → GitHub → Internal

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│  EXTERNAL PC (Development)                               │
│  - Windows PC at home/office                             │
│  - Development environment                               │
│  - Mock services for testing                             │
│  - Safe to experiment                                    │
│                                                           │
│  Branch: main                                            │
│  .env: Development configuration                         │
└──────────────┬───────────────────────────────────────────┘
               │
               │ git push origin main
               ↓
┌──────────────────────────────────────────────────────────┐
│  GITHUB REPOSITORY                                       │
│  https://github.com/Martinb113/J_askattdocsUI.git       │
│                                                           │
│  Branch: main (production-ready code)                    │
│  Contains: Code, documentation, configuration templates  │
│  Excludes: .env files, sensitive data, local configs     │
└──────────────┬───────────────────────────────────────────┘
               │
               │ git pull origin main
               ↓
┌──────────────────────────────────────────────────────────┐
│  INTERNAL SERVER (Testing/Production)                    │
│  - Company server                                        │
│  - Real Azure AD authentication                          │
│  - Real company databases and APIs                       │
│  - Production configuration                              │
│                                                           │
│  Branch: main                                            │
│  .env: Production configuration (SENSITIVE!)             │
└──────────────────────────────────────────────────────────┘
```

---

## 📅 Daily Workflows

### **Workflow A: Development on External PC** (Most Common)

**Scenario**: You're developing a new feature or fixing a bug

```bash
# 1. Start work (if continuing from previous day)
cd C:\Users\admin\Documents\AI_projects\j_askdocs
git status  # Check current state

# 2. Pull latest changes (if any from internal issues)
git pull origin main

# 3. Develop and test locally
# ... make code changes ...
# ... test with mock services ...

# 4. Review changes before committing
git status  # See what files changed
git diff    # Review actual changes

# 5. Commit changes
git add .
git commit -m "Feature: Descriptive message about what you did"

# 6. Push to GitHub
git push origin main
```

**What happens next**: Internal server can pull these changes when ready

---

### **Workflow B: Update Internal Server** (Daily or as needed)

**Scenario**: You want to test latest code on internal server with real data

```bash
# On Internal Server

# 1. Navigate to project directory
cd /path/to/j_askdocs

# 2. Check current status (should be clean)
git status

# 3. Pull latest changes from GitHub
git pull origin main

# 4. Check if .env file is still intact
ls -la backend/.env  # Should exist and contain company config

# 5. Restart services to apply changes
# ... restart backend and frontend ...

# 6. Test with real company resources
# ... manual testing ...
```

**Important**: Your `.env` file stays untouched during `git pull` because it's in `.gitignore`

---

### **Workflow C: Quick Fix on External After Internal Testing** (Common Loop)

**Scenario**: Internal server found an issue, you need to fix it quickly

```bash
# On External PC

# 1. Note the issue (mental note or quick text file locally)
# Example: "Login fails with 'Invalid token' error"

# 2. Reproduce issue locally if possible
# ... try to recreate the problem ...

# 3. Fix the code
# ... edit files ...

# 4. Test locally
# ... verify fix works ...

# 5. Commit and push
git add .
git commit -m "Fix: Login token validation for Azure AD"
git push origin main

# 6. Notify internal server / Pull on internal server
```

---

### **Workflow D: Emergency Fix on Internal** (Rare, Use with Caution)

**Scenario**: Critical bug on internal server, need immediate fix, can't wait for external

⚠️ **WARNING**: Only use this if absolutely necessary!

```bash
# On Internal Server

# 1. Make the minimal code change
# ... fix the critical bug ...

# 2. Test immediately
# ... verify fix works ...

# 3. Document what you did
# Create a text file with exact changes made

# 4. DON'T PUSH from internal!

# 5. Recreate the same fix on External PC later
# ... manually apply same changes on external ...

# 6. Push from External
# External: git add . && git commit && git push
```

**Better Alternative**: Use Workflow C instead - fix on External first

---

## 🔄 Synchronization Patterns

### **Pattern 1: Daily Sync (Recommended)**

```
Morning (External PC):
  - git pull origin main
  - Check if any issues were noted
  - Continue development

Evening (External PC):
  - Commit and push day's work
  - git push origin main

Night/Next Morning (Internal Server):
  - git pull origin main
  - Test with production config
  - Note any issues for External PC
```

### **Pattern 2: Continuous Development**

```
External PC (Throughout the day):
  - Develop → Commit → Push (multiple times)
  - Each logical change gets committed
  
Internal Server (Periodic):
  - Pull updates when ready to test
  - Not every push needs internal testing
  - Focus on testing complete features
```

### **Pattern 3: Feature-Based Sync**

```
External PC:
  - Develop entire feature
  - Test thoroughly locally
  - Commit as logical chunks
  - Push when feature is complete
  
Internal Server:
  - Pull after feature completion
  - Comprehensive testing
  - Validate with real data
```

---

## 🔍 What Gets Committed vs Ignored

### **✅ COMMITTED TO GIT (Safe to Share)**

```
✅ Source code (.py, .tsx, .ts, .js)
✅ Configuration templates (.env.example)
✅ Documentation (.md files)
✅ Dependencies (requirements.txt, package.json)
✅ Database migrations (alembic/versions/*.py)
✅ Docker configurations (Dockerfile, docker-compose.yml)
✅ Scripts (seed_data.py, etc.)
✅ Tests (tests/*.py)
```

### **❌ NEVER COMMITTED (Sensitive/Local)**

```
❌ .env files (actual configuration)
❌ database files (*.db)
❌ __pycache__ / node_modules
❌ Virtual environments (venv/, .venv/)
❌ IDE settings (.vscode/, .idea/)
❌ Log files (*.log)
❌ Temporary files (*.tmp, *.temp)
❌ User data backups
❌ Company-specific credentials
```

---

## 🛡️ Safety Protocols

### **Before EVERY Push from Internal** (If you must)

1. ⚠️ **STOP** - Is this really necessary?
2. 📋 Run `git status` - Review all changed files
3. 🔍 Run `git diff` - Review every line of changes
4. 🔒 Check for sensitive data:
   - Database passwords
   - API keys
   - Internal URLs
   - Company-specific credentials
   - User data
5. ✅ Only push if 100% certain it's safe

### **Before EVERY Push from External** (Routine)

1. 📋 Run `git status` - Quick review
2. 💬 Write descriptive commit message
3. 🚀 Push freely (this environment is safe)

### **Weekly Security Check**

```bash
# Check .gitignore is working
git status  # Should not show .env files

# Verify .env is ignored
git check-ignore backend/.env  # Should return the path

# Review recent commits for accidents
git log --oneline -10

# Check what's being tracked
git ls-files | grep -E '\\.env$|\\.db$'  # Should return nothing
```

---

## 🐛 Common Issues and Solutions

### **Issue 1: ".env file disappeared after git pull"**

**Cause**: You accidentally committed .env and then it got removed in a later commit

**Solution**:
```bash
# Your .env was never removed, it's still there
ls -la backend/.env

# If it's really gone, recreate from template
cp backend/.env.internal.example backend/.env
# Edit with your credentials
```

### **Issue 2: "Merge conflict in .env file"**

**Cause**: .env shouldn't be in Git in the first place

**Solution**:
```bash
# Check if .env is being tracked (it shouldn't be)
git ls-files | grep .env

# If it is, remove it from tracking
git rm --cached backend/.env
git commit -m "Remove .env from version control"

# Add to .gitignore (should already be there)
echo "backend/.env" >> .gitignore
git add .gitignore
git commit -m "Ensure .env is in .gitignore"
```

### **Issue 3: "Changes on internal not showing on external"**

**Cause**: Forgot to push from internal (or shouldn't push from internal anyway)

**Solution**:
```bash
# On internal: Don't push, recreate changes on external instead
# Make a note of what changed

# On external: Recreate the changes
git add .
git commit -m "Recreate fix from internal testing"
git push origin main
```

### **Issue 4: "Git says 'already up to date' but I made changes"**

**Cause**: Changes not committed

**Solution**:
```bash
# Check for uncommitted changes
git status

# Commit them
git add .
git commit -m "Description"
git push origin main
```

---

## 📝 Commit Message Guidelines

### **Good Commit Messages**

```
✅ "Feature: Add streaming chat response with SSE"
✅ "Fix: Azure AD token validation in auth service"
✅ "Update: Database schema for conversation history"
✅ "Refactor: Extract authentication logic to service layer"
✅ "Docs: Add environment setup guide"
✅ "Chore: Update dependencies to latest versions"
```

### **Bad Commit Messages**

```
❌ "Update"
❌ "Fix stuff"
❌ "asdf"
❌ "WIP"
❌ "test"
```

### **Commit Message Format**

```
Type: Brief description (50 chars or less)

Optional longer explanation of what and why
(wrap at 72 characters)

- Bullet points for specific changes
- Another change
- Yet another change
```

**Types**:
- `Feature:` - New functionality
- `Fix:` - Bug fix
- `Update:` - Update existing functionality
- `Refactor:` - Code restructuring without behavior change
- `Docs:` - Documentation only
- `Chore:` - Maintenance tasks (dependencies, config)
- `Test:` - Adding or updating tests

---

## 🚀 Quick Command Reference

### **Daily Commands**

```bash
# Check status
git status

# Pull latest
git pull origin main

# Review changes
git diff

# Commit everything
git add .
git commit -m "Type: Message"

# Push to GitHub
git push origin main

# View recent commits
git log --oneline -5
```

### **Safety Commands**

```bash
# See what's being tracked
git ls-files

# Check if .env is ignored
git check-ignore backend/.env

# See detailed diff
git diff --staged

# Undo last commit (before push)
git reset --soft HEAD~1
```

### **Troubleshooting Commands**

```bash
# See full status
git status -v

# See all branches
git branch -a

# Check remote URL
git remote -v

# Force overwrite local changes
git reset --hard origin/main
```

---

## 📊 Decision Tree

**Where should I make this change?**

```
Is it a code change?
├─ YES → Make on External PC
│         - Safer environment
│         - Can push freely
│         - Better development tools
│
└─ NO → Is it configuration?
    ├─ YES → Edit .env file locally
    │         - Never commit .env
    │         - Each environment has own .env
    │
    └─ NO → Is it documentation?
        └─ YES → Can do on either
                  - Safe to share
                  - No sensitive data
```

**Should I push this commit?**

```
Where am I working?
├─ External PC → YES, push freely ✅
│
└─ Internal Server → STOP! ⚠️
    └─ Does it contain ANY sensitive data?
        ├─ YES → DON'T PUSH ❌
        │         Recreate on External instead
        │
        └─ NOT SURE → DON'T PUSH ❌
                       Better safe than sorry
```

---

## 🎓 Learning Resources

### **Git Basics**
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

### **Security**
- [Removing Sensitive Data from Git](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [.gitignore Best Practices](https://www.atlassian.com/git/tutorials/saving-changes/gitignore)

### **Workflow Patterns**
- [Git Best Practices](https://www.atlassian.com/git/tutorials/comparing-workflows)

---

## ✅ Workflow Checklist

**Starting Your Day:**
- [ ] Open project directory
- [ ] Run `git status` to check current state
- [ ] Run `git pull origin main` to get latest changes
- [ ] Review what changed (if anything)
- [ ] Start development

**During Development:**
- [ ] Make logical, small commits
- [ ] Test changes locally
- [ ] Write descriptive commit messages
- [ ] Push completed features/fixes

**Ending Your Day:**
- [ ] Commit any work in progress
- [ ] Push to GitHub if changes are complete
- [ ] Update any documentation if needed
- [ ] Note any issues for next day

**Before Pushing (Internal Server):**
- [ ] REALLY necessary?
- [ ] Reviewed `git status`?
- [ ] Reviewed `git diff`?
- [ ] No sensitive data?
- [ ] 100% certain it's safe?

---

**Next Steps**: See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for configuring your .env files

