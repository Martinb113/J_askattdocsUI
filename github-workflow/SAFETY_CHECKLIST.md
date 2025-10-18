# Safety Checklist

**Purpose**: Prevent accidental commit of sensitive data to GitHub  
**When to Use**: Before EVERY push from Internal Server

---

## 🚨 Critical Rules

### **Golden Rules (NEVER Break These)**

1. 🔒 **NEVER commit `.env` files** - They contain sensitive credentials
2. 🔒 **NEVER commit database files** - They contain user data
3. 🔒 **NEVER commit backup files** - They may contain sensitive data
4. 🔒 **NEVER commit API keys or passwords** - Even in comments or docs
5. 🔒 **NEVER commit company-specific internal URLs** - Security risk

### **Safe Practice Rules**

1. ✅ **ALWAYS work on External PC for code changes** - Safer environment
2. ✅ **ALWAYS review `git status` before committing** - Know what you're adding
3. ✅ **ALWAYS review `git diff` before pushing** - Review every line
4. ✅ **ALWAYS use .env files for configuration** - Keep sensitive data separate
5. ✅ **ALWAYS test locally before pushing** - Catch issues early

---

## 📋 Pre-Push Checklist

### **For External PC** (Quick Check ✅)

External PC is your safe development environment. Quick check is sufficient:

```bash
# 1. Review what's being committed
git status

# 2. Quick scan for obvious issues
# - No .env files?
# - No .db files?
# - Looks good?

# 3. Push freely
git push origin main
```

**Why it's safe**: External PC doesn't have production credentials or sensitive data.

---

### **For Internal Server** (STRICT CHECK ⚠️)

⚠️ **WARNING**: Only push from Internal Server if absolutely necessary!

**Step 1: Question Yourself**

- [ ] Do I really need to push from Internal Server?
- [ ] Can I make this change on External PC instead?
- [ ] Is this just an issue documentation (safer)?
- [ ] Am I 100% certain this is safe?

**If you answered "NO" to any question** → **STOP! Work on External PC instead.**

---

**Step 2: Review File List** (5 minutes minimum)

```bash
# Show all files that will be committed
git status

# Review EACH file carefully:
```

**Check for these dangerous files:**
```bash
❌ .env
❌ .env.local
❌ .env.production
❌ *.db (database files)
❌ *.sqlite
❌ *.backup
❌ dump.sql
❌ *.pem, *.key (certificates)
❌ credentials.json
❌ secrets.yaml
❌ config.prod.yml
```

**If ANY of these appear** → **STOP! Remove them from commit.**

---

**Step 3: Review File Contents** (10+ minutes)

```bash
# Show detailed diff of all changes
git diff --cached

# Or review each file individually
git diff --cached backend/app/config.py
git diff --cached backend/app/services/auth.py
```

**For EACH changed file, look for:**

❌ **Database Credentials**
```python
# BAD - Don't commit this!
DATABASE_URL = "postgresql://admin:P@ssw0rd123@db.company.local:5432/prod"
MONGO_URI = "mongodb://user:pass@mongo.internal:27017/app"
```

❌ **API Keys & Secrets**
```python
# BAD - Don't commit this!
API_KEY = "sk_live_abc123xyz789"
SECRET_KEY = "supersecretkey123"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

❌ **Internal URLs & IPs**
```python
# BAD - Don't commit this!
INTERNAL_API_URL = "http://10.0.1.50:8080/api"
COMPANY_SERVER = "internal-server.company.local"
```

❌ **User Data**
```python
# BAD - Don't commit this!
test_users = [
    {"email": "john.doe@company.com", "password": "pass123"},
    {"email": "real.user@company.com", "token": "xyz789"}
]
```

❌ **Hardcoded Credentials in Code**
```python
# BAD - Don't commit this!
def connect_to_db():
    return psycopg2.connect(
        host="db.company.local",
        user="admin",
        password="CompanyPass2024"
    )
```

✅ **GOOD - Safe to commit**
```python
# Uses environment variables (safe!)
def connect_to_db():
    return psycopg2.connect(settings.database_url)

# Environment-aware code (safe!)
if settings.environment == "production":
    api = ProductionAPI()
else:
    api = MockAPI()

# Configuration template (safe!)
# .env.example
DATABASE_URL=postgresql://user:password@host:5432/db
API_KEY=your_api_key_here
```

---

**Step 4: Check for Common Mistakes**

```bash
# 1. Verify .env is not being tracked
git ls-files | grep -E '\\.env$'
# Should return NOTHING

# 2. Verify no database files
git ls-files | grep -E '\\.(db|sqlite|sqlite3)$'
# Should return NOTHING

# 3. Check what's in .gitignore
cat .gitignore | grep -E '\\.env|venv|\\.db'
# Should see .env, venv/, *.db, etc.

# 4. Double-check staged changes
git diff --staged --name-only
# Review each file name carefully
```

---

**Step 5: Search for Sensitive Patterns**

```bash
# Search for potential passwords in staged changes
git diff --cached | grep -iE 'password|passwd|pwd'

# Search for potential API keys
git diff --cached | grep -iE 'api[_-]?key|secret[_-]?key|token'

# Search for potential database URLs
git diff --cached | grep -iE 'postgresql://|mongodb://|mysql://'

# Search for internal IPs
git diff --cached | grep -E '10\\.0\\.|192\\.168\\.|172\\.16\\.'
```

**If ANY matches found** → **REVIEW CAREFULLY!**

---

**Step 6: Final Confirmation**

Before pushing, answer these questions honestly:

- [ ] I reviewed `git status` - all files are intentional
- [ ] I reviewed `git diff` - every line is safe to share
- [ ] No .env files are being committed
- [ ] No database files are being committed
- [ ] No passwords or API keys in code
- [ ] No internal URLs or IP addresses
- [ ] No user data or PII
- [ ] No company secrets or proprietary info
- [ ] I would be comfortable if this was posted publicly
- [ ] I am 100% certain this is safe

**If you answered "NO" to ANY question** → **DO NOT PUSH!**

---

**Step 7: Push (Only if all checks passed)**

```bash
# One final review
git log -1 --stat
# Shows the commit you're about to push

# Push to GitHub
git push origin main

# Immediately verify what was pushed
git log origin/main -1
```

---

## 🔧 Emergency: I Accidentally Committed Sensitive Data!

### **If You Haven't Pushed Yet** (Easy Fix ✅)

```bash
# Option 1: Remove the file from staging
git reset HEAD backend/.env
# File stays on disk, just not committed

# Option 2: Undo the last commit completely
git reset --soft HEAD~1
# Changes stay, commit is undone

# Option 3: Amend the last commit
# Remove sensitive file, then:
git add .
git commit --amend
```

---

### **If You Already Pushed** (Serious! ⚠️)

**STOP! Follow these steps immediately:**

**Step 1: Remove the sensitive data from history**

```bash
# WARNING: This rewrites Git history!
# Only do this if you're the only one working on the repository

# Remove a specific file from all history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (rewrites remote history)
git push origin main --force
```

**Step 2: Rotate all exposed credentials**

If you exposed:
- **Database password** → Change it immediately in database server
- **API keys** → Revoke and generate new ones
- **SECRET_KEY** → Generate new one, users will be logged out
- **Azure AD secret** → Revoke in Azure Portal, create new one

**Step 3: Inform security team**

If this is a company repository:
- Notify IT/Security team immediately
- Document what was exposed and when
- Document what credentials were rotated
- Review access logs for any unauthorized access

---

## 🛡️ Prevention Strategies

### **Strategy 1: Use .gitignore (Essential)**

Verify your `.gitignore` is comprehensive:

```bash
# Check current .gitignore
cat .gitignore

# Should include at minimum:
# Environment files
.env
.env.local
.env.production
.env.*.local

# Database files
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.py[cod]
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```

**Add missing patterns:**
```bash
echo "*.db" >> .gitignore
echo ".env*" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore for better security"
```

---

### **Strategy 2: Set Up Pre-Commit Hook** (Recommended)

See [PRE_COMMIT_HOOKS.md](PRE_COMMIT_HOOKS.md) for detailed setup.

Quick setup:
```bash
# Create hook script
nano .git/hooks/pre-commit

# Add the script (see PRE_COMMIT_HOOKS.md)

# Make executable
chmod +x .git/hooks/pre-commit
```

---

### **Strategy 3: Regular Security Audits**

**Weekly check** (5 minutes):

```bash
# 1. Check what's being tracked by Git
git ls-files > tracked_files.txt
grep -E '\\.env|password|secret|credentials' tracked_files.txt
# Should be empty

# 2. Search for hardcoded secrets in code
grep -r "password\s*=\s*['\"]" backend/app/
# Should return nothing or only examples/comments

# 3. Review recent commits
git log --oneline -20
# Look for suspicious commit messages
```

---

### **Strategy 4: Work on External PC**

**Best prevention: Do all development on External PC**

```
External PC:
  ✅ No sensitive data
  ✅ Can push freely
  ✅ Better development environment
  ✅ Easier to experiment
  ✅ No security risk

Internal Server:
  ⚠️ Has sensitive data
  ⚠️ Should rarely push
  ⚠️ Requires careful checks
  ⚠️ Risk of accidents
  ⚠️ Security concern
```

**Golden Rule**: Internal Server → Pull only, External PC → Push freely

---

## 📝 Safe Commit Examples

### ✅ SAFE Commits (Can push freely)

```bash
# Feature development
git commit -m "Feature: Add streaming chat with SSE"
# ✅ New functionality, no sensitive data

# Bug fix
git commit -m "Fix: Correct token validation logic"
# ✅ Code improvement, no credentials

# Refactoring
git commit -m "Refactor: Extract auth service logic"
# ✅ Code organization, no secrets

# Documentation
git commit -m "Docs: Add API endpoint documentation"
# ✅ Documentation, no sensitive info

# Configuration template
git commit -m "Add .env.example with configuration template"
# ✅ Template only, no real credentials

# Tests
git commit -m "Test: Add unit tests for auth service"
# ✅ Test code, uses mock data
```

### ❌ UNSAFE Commits (NEVER push these)

```bash
# Actual configuration
git commit -m "Add production .env"
# ❌ Contains real credentials!

# Database dump
git commit -m "Add database backup"
# ❌ Contains user data!

# Hardcoded credentials
git commit -m "Quick fix: Add database connection"
# ❌ Might contain hardcoded password

# Company-specific
git commit -m "Configure internal API endpoints"
# ❌ Might expose internal infrastructure

# Debug code
git commit -m "Debug: Print API keys for testing"
# ❌ Temporary code that exposes secrets
```

---

## 🎯 Quick Decision Tree

**Should I commit this file?**

```
Is it a .env file?
├─ YES → ❌ NO! Never commit .env
│
├─ NO → Is it a database file?
│   ├─ YES → ❌ NO! Never commit databases
│   │
│   └─ NO → Does it contain passwords/keys?
│       ├─ YES → ❌ NO! Refactor to use .env
│       │
│       └─ NO → Is it source code?
│           ├─ YES → ✅ Probably safe
│           │         (but still review diff!)
│           │
│           └─ NO → Is it documentation?
│               ├─ YES → ✅ Safe if no secrets
│               │
│               └─ NO → ⚠️ Review carefully
```

**Should I push from Internal Server?**

```
Where should this change be made?
├─ External PC → ✅ Make change there instead
│                    Much safer!
│
└─ Internal only → Why?
    ├─ Fixing bug → ⚠️ Can you reproduce on External?
    │   ├─ YES → ✅ Fix on External instead
    │   └─ NO → ⚠️ Document issue, fix on External
    │
    ├─ Adding config → ❌ Config goes in .env (not committed)
    │
    └─ Documentation → ✅ Might be OK
                          Review carefully for company secrets
```

---

## 📞 When In Doubt

**If you're uncertain whether something is safe to commit:**

1. ❌ **DON'T commit it**
2. 🤔 **Ask yourself**: "Would I be comfortable if this was public?"
3. 💭 **Think**: "Does this contain any company-specific information?"
4. 🔄 **Alternative**: Make the change on External PC instead
5. 📝 **Document**: Write down the change needed, implement on External PC

**Remember**: It's always better to be too cautious than to accidentally expose sensitive data!

---

## ✅ Daily Security Checklist

**Every Day Before Starting Work:**
- [ ] Working on External PC (safer) not Internal Server
- [ ] .env file is in .gitignore
- [ ] .env file is NOT tracked by Git

**Before Every Commit:**
- [ ] Reviewed `git status`
- [ ] Reviewed `git diff`
- [ ] No sensitive data in changes
- [ ] Meaningful commit message

**Before Every Push (from Internal):**
- [ ] Really necessary to push from Internal?
- [ ] All checks from "Pre-Push Checklist" completed
- [ ] 100% certain it's safe
- [ ] No company secrets exposed

**Weekly:**
- [ ] Audit tracked files for sensitive data
- [ ] Review recent commits
- [ ] Check .gitignore is comprehensive
- [ ] Rotate development secrets if exposed

---

**Next Steps**: See [PRE_COMMIT_HOOKS.md](PRE_COMMIT_HOOKS.md) for automated safety checks

