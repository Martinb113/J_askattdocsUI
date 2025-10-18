# Initial Setup Instructions

## 🎯 One-Time Setup

Follow these steps to establish the workflow on both machines.

---

## 📍 Step 1: Create Develop Branch

**Run this ONCE on External PC:**

```bash
# Make sure you're on main
git checkout main
git pull origin main

# Create develop branch from main
git checkout -b develop

# Push develop to GitHub
git push -u origin develop
```

Now both `main` and `develop` exist on GitHub.

---

## 💻 Step 2: Setup External PC

### 2.1 Configure Git (if not already done)

```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch behavior
git config --global pull.rebase false
```

### 2.2 Clone or Update Repository

**If new clone:**
```bash
git clone https://github.com/Martinb113/J_askattdocsUI.git
cd J_askattdocsUI
git checkout develop
```

**If already cloned:**
```bash
cd J_askattdocsUI
git fetch origin
git checkout develop
git pull origin develop
```

### 2.3 Setup Environment

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit with external/development settings
# nano backend/.env
# or use your preferred editor
```

### 2.4 Verify .gitignore

```bash
# Check .gitignore includes these:
cat .gitignore | grep -E '(\.env|\.db|\.log)'

# Should see:
# .env
# *.db
# *.log
# (and others)
```

---

## 🏢 Step 3: Setup Internal Server

### 3.1 Clone Repository

```bash
# Clone the repository
git clone https://github.com/Martinb113/J_askattdocsUI.git
cd J_askattdocsUI
```

### 3.2 Choose Branch Strategy

**Option A: Production Only (Recommended for safety)**
```bash
# Stay on main branch for production
git checkout main
```

**Option B: Testing Development Versions**
```bash
# Use develop branch for testing
git checkout develop
```

### 3.3 Setup Environment (CRITICAL)

```bash
# Copy internal environment template
cp backend/.env.example backend/.env

# Edit with INTERNAL/PRODUCTION settings
# nano backend/.env

# Configure:
# - Internal database connection
# - Company Azure AD credentials
# - Internal API URLs
# - Production secret keys
```

### 3.4 Verify Security

```bash
# CRITICAL: Verify .env is NOT tracked by git
git status

# Should NOT show .env file
# If it does, STOP and add to .gitignore
```

---

## 🔒 Step 4: Verify .gitignore

Ensure `.gitignore` contains:

```
# Environment variables
.env
.env.*
!.env.example
!.env.*.example

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Python
__pycache__/
*.py[cod]
venv/
.venv/

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Sensitive
*.key
*.pem
secrets/
```

---

## 🔐 Step 5: Setup Pre-commit Protection (Optional but Recommended)

### On both machines:

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Check for .env files being committed
if git diff --cached --name-only | grep -E '^\.env$|\.env\.production|\.env\.local'; then
    echo "❌ ERROR: Attempting to commit environment file!"
    echo "Environment files contain sensitive data."
    echo "Only .env.example files should be committed."
    exit 1
fi

# Check for database files
if git diff --cached --name-only | grep -E '\.db$|\.sqlite$'; then
    echo "❌ ERROR: Attempting to commit database file!"
    echo "Database files should not be in version control."
    exit 1
fi

echo "✓ Pre-commit checks passed"
exit 0
EOF

# Make it executable
chmod +x .git/hooks/pre-commit

# Test it
git add backend/.env  # This should fail
# Should see error message
git reset HEAD backend/.env  # Undo
```

---

## 🌿 Step 6: Setup Branch Protection (GitHub - Optional)

**On GitHub.com (if you want extra safety):**

1. Go to repository settings
2. Click "Branches"
3. Add branch protection rule for `main`:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass
   - ✅ Include administrators (if working with team)

This prevents accidental direct pushes to `main`.

---

## ✅ Step 7: Verify Setup

### On External PC:

```bash
# Check branches
git branch -a
# Should see:
# * develop
#   main
#   remotes/origin/develop
#   remotes/origin/main

# Check .env is ignored
git status
# Should NOT show .env file

# Check remote URL
git remote -v
# Should show your GitHub repository
```

### On Internal Server:

```bash
# Check branch
git branch
# Should show: * main (or * develop)

# Check .env exists and is ignored
ls backend/.env    # Should exist
git status         # Should NOT show .env

# Verify .env has internal settings
cat backend/.env | grep ENVIRONMENT
# Should show: ENVIRONMENT=internal
```

---

## 🧪 Step 8: Test the Workflow

### On External PC:

```bash
# Create test feature
git checkout develop
git checkout -b feature/test-workflow

# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test: Workflow verification"
git push -u origin feature/test-workflow

# Merge to develop
git checkout develop
git merge feature/test-workflow
git push origin develop

# Check it worked
git log --oneline -5
```

### On Internal Server:

```bash
# Pull the test change
git checkout develop
git pull origin develop

# Check it arrived
git log --oneline -5

# Should see your test commit

# Switch back to production if using main
git checkout main
```

---

## 📋 Post-Setup Checklist

- [ ] `develop` branch created and pushed to GitHub
- [ ] External PC has both `main` and `develop` branches
- [ ] Internal Server has repository cloned
- [ ] `.env` files created on both machines (different settings)
- [ ] `.env` files confirmed NOT tracked by git
- [ ] `.gitignore` properly configured
- [ ] Pre-commit hooks installed (optional)
- [ ] Test workflow completed successfully

---

## 🆘 Troubleshooting

### "Branch 'develop' not found"

```bash
git fetch origin
git checkout develop
```

### ".env file showing in git status"

```bash
# Add to .gitignore
echo ".env" >> .gitignore

# Remove from tracking (if was added)
git rm --cached backend/.env

# Commit .gitignore update
git add .gitignore
git commit -m "Update .gitignore to ignore .env files"
```

### "Permission denied" on Internal Server

```bash
# Setup SSH keys or use HTTPS with credentials
# SSH: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
# HTTPS: Git will prompt for username/password or token
```

### "Merge conflicts" during setup

```bash
# If conflicts occur during initial setup:
git merge --abort
# Contact for help - shouldn't happen in fresh setup
```

---

**Next Steps:** After setup is complete, refer to:
- `external-workflow.md` for development workflow
- `internal-workflow.md` for production deployment
- `safety-checklist.md` before any push

---

**Setup Complete!** 🎉 You're ready to use the workflow.

