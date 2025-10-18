# Internal Server Workflow

**Environment:** Company production server  
**Safety Level:** CRITICAL (contains sensitive data)  
**Primary Role:** Testing, adjustments, production deployment  
**CAN PUSH:** Yes, to `internal` branch only (with safety checks)

---

## ⚠️ CRITICAL RULES

1. ✅ **CAN push to `internal` branch** (production fixes/adjustments)
2. ❌ **NEVER push .env files or sensitive data**
3. ✅ **Test with production configuration**
4. ✅ **Pull `develop` for testing new features**
5. ✅ **Pull `main` for production deployment**

---

## 🔄 Daily Operations

### Pull Latest Development for Testing

```bash
git checkout develop
git pull origin develop

# Test with production .env settings
# Report results to External PC
```

### Deploy Stable Production Version

```bash
git checkout main
git pull origin main

# Restart services
# Monitor production
```

---

## 🛠️ Making Changes (NEW - You CAN Push!)

### Scenario 1: Found Bug During Testing

```bash
# Pull latest develop
git checkout develop
git pull origin develop

# Create/switch to internal branch
git checkout -b internal  # First time
# OR
git checkout internal     # If exists
git pull origin internal

# Make the fix
# ... edit code ...

# Commit with clear message
git add backend/app/api/v1/auth.py  # Only specific files
git commit -m "Fix: Production Azure AD token validation"

# SAFETY CHECK before push (see checklist below)
git status
git diff HEAD~1

# If safe, push
git push origin internal
```

### Scenario 2: Production Environment Adjustments

```bash
git checkout internal
git pull origin internal

# Make production-specific adjustments
# ... edit code ...

git add backend/app/config.py
git commit -m "Adjust: Database connection pool for production load"
git push origin internal
```

### Scenario 3: Quick Production Hotfix

```bash
git checkout internal
git pull origin internal

# Emergency fix
# ... edit code ...

git add <critical-file>
git commit -m "Hotfix: Critical production issue - [description]"
git push origin internal

# Notify External PC immediately
```

---

## 🚨 PRE-PUSH SAFETY CHECKLIST

**Before EVERY push from Internal Server:**

```bash
# 1. Review what you're pushing
git status

# 2. Check file contents
git diff

# 3. Verify staged files
git diff --staged

# 4. Ask yourself:
```

- [ ] No `.env` files?
- [ ] No database files?
- [ ] No log files with real data?
- [ ] No user/customer data?
- [ ] No company secrets/credentials?
- [ ] No internal IP addresses/URLs in code?
- [ ] Only code fixes?

**If ALL checkboxes ✅ → Safe to push**  
**If ANY checkbox ❌ → DO NOT PUSH**

---

## ✅ SAFE to Push

```
✅ Code fixes (bugs, logic errors)
✅ Production-specific adjustments
✅ Configuration code (not .env files)
✅ Test results documentation
✅ Performance optimizations
```

## ❌ NEVER Push

```
❌ .env files
❌ *.db, *.sqlite files
❌ Log files with real data
❌ Backup files
❌ User/customer data
❌ API keys, passwords in code
❌ Internal URLs hardcoded
```

---

## 🔄 Typical Workflows

### Workflow A: Test Passes, No Changes

```bash
git checkout develop
git pull origin develop
# Test...
# Works perfectly!
# Report to External PC: "All tests pass ✓"
# Done - no push needed
```

### Workflow B: Test Fails, Need Fix

```bash
git checkout develop
git pull origin develop
# Test... fails!

git checkout internal
# Make fix
git add <files>
git commit -m "Fix: [issue]"
# Safety check!
git push origin internal
# Report: "Fixed on internal branch, please review"
```

### Workflow C: Production Deployment

```bash
git checkout main
git pull origin main
# Deploy to production
# Monitor...
# All good!
```

---

## 🔍 Checking Changes Before Pull

```bash
# See what will change
git fetch origin develop
git log HEAD..origin/develop --oneline

# See code changes
git diff HEAD..origin/develop

# If looks safe, pull
git pull origin develop
```

---

## 🆘 Emergency Rollback

```bash
# See recent commits
git log --oneline -10

# Rollback to previous commit
git checkout HEAD~1

# Or rollback to specific commit
git checkout <commit-hash>

# To return to latest
git checkout main  # or develop
```

---

## 📊 Branch Management

```bash
# See current branch
git branch

# Switch branches
git checkout main       # Production
git checkout develop    # Testing
git checkout internal   # Your changes

# Update branch
git pull origin <branch-name>

# See all branches
git branch -a
```

---

## 🔐 Protecting Sensitive Data

### Verify .env is Ignored

```bash
git status  # Should NOT show .env

# If it shows .env, DON'T push!
git reset HEAD .env
```

### If Accidentally Staged Sensitive File

```bash
# Unstage immediately
git reset HEAD <sensitive-file>

# Or unstage everything
git reset HEAD .
```

---

## 💡 Best Practices

1. **Small, focused commits** - One fix per commit
2. **Clear commit messages** - "Fix: Auth token validation"
3. **Always safety check** - Review before push
4. **Keep internal branch clean** - Production fixes only
5. **Report changes** - Notify External PC after push
6. **Test thoroughly** - Don't push broken code

---

## ⚡ Quick Commands

```bash
# Test latest development
git checkout develop
git pull origin develop

# Make changes
git checkout internal
git add <files>
git commit -m "Description"
git push origin internal

# Deploy production
git checkout main
git pull origin main

# Emergency rollback
git checkout HEAD~1
```

---

## 🎯 Decision Tree

```
Need to make changes?
  │
  ├─ No → Just test and report
  │
  └─ Yes → Is it production-specific fix?
      │
      ├─ Yes → Use internal branch
      │   └─ git checkout internal
      │       git add <files>
      │       SAFETY CHECK
      │       git push origin internal
      │
      └─ No → Report issue to External PC
          └─ Let External PC fix in develop
```

---

**Remember:** You CAN push to `internal` branch, but ALWAYS do safety check first. When in doubt, don't push - report to External PC instead.
