# GitHub Workflow Guide

## 🎯 Quick Reference

**Branch Structure (Dual-Track):**
```
main (production) ← Protected, merge only after review
  ↑
  ├── develop (External PC work)
  │     ↑
  │     └── feature/* (daily development)
  │
  └── internal (Internal Server fixes)
        ↑
        └── Production adjustments & fixes
```

**Key Principle:** 
- External PC → `develop` branch
- Internal Server → `internal` branch  
- Both merge to `main` after review & alignment

---

## 📚 Documentation Files

1. **[branch-strategy.md](branch-strategy.md)** - Dual-track branch structure
2. **[external-workflow.md](external-workflow.md)** - Development on External PC
3. **[internal-workflow.md](internal-workflow.md)** - Testing & fixes on Internal Server
4. **[merge-alignment-guide.md](merge-alignment-guide.md)** - Align branches before production
5. **[safety-checklist.md](safety-checklist.md)** - Pre-push security checks
6. **[conflict-resolution.md](conflict-resolution.md)** - Resolve merge conflicts
7. **[setup-instructions.md](setup-instructions.md)** - Initial setup
8. **[environment-config-guide.md](environment-config-guide.md)** - Manage .env files
9. **[quick-reference.md](quick-reference.md)** - Command cheat sheet
10. **[visual-workflow.md](visual-workflow.md)** - Diagrams

**Start:** [INDEX.md](INDEX.md) - Full navigation

---

## ⚡ Common Commands

### External PC (Development)

```bash
# Start feature
git checkout develop
git pull origin develop
git checkout -b feature/name
# ... work ...
git add .
git commit -m "Description"
git push origin feature/name

# Merge to develop
git checkout develop
git merge feature/name
git push origin develop

# Promote to production (simple case)
git checkout main
git merge develop
git push origin main
```

### Internal Server (Testing & Fixes)

```bash
# Test new features
git checkout develop
git pull origin develop
# ... test ...

# Make production fixes
git checkout internal
git pull origin internal
# ... fix ...
git add <files>
# SAFETY CHECK!
git commit -m "Fix: description"
git push origin internal

# Deploy production
git checkout main
git pull origin main
```

### Alignment (External PC)

```bash
# When both develop & internal have changes
git checkout develop
git pull origin develop
git pull origin internal
git merge internal
# ... test merged code ...
git checkout main
git merge develop
git push origin main
```

---

## 🚨 Golden Rules

1. ✅ External PC pushes to `develop` (and `feature/*`)
2. ✅ Internal Server pushes to `internal` (with safety checks)
3. ✅ Merge both to `main` after review & alignment
4. ✅ Check safety-checklist.md before any push from Internal
5. ❌ Never push directly to `main`
6. ❌ Never commit .env files

---

## 🔄 Complete Flow

```
Day 1-3: External PC
  feature/auth → develop → push to GitHub

Day 4: Internal Server  
  Pull develop → test → find issue
  Switch to internal → fix → push to GitHub

Day 5: External PC (Alignment)
  Pull both develop + internal
  Merge internal → develop
  Test merged code
  Promote develop → main

Day 5: Internal Server (Deploy)
  Pull main → production deployment
```

---

## 🎯 Quick Decision Guide

**"Where should I push my changes?"**

- External PC, new feature? → `develop`
- Internal Server, production fix? → `internal`
- Production release? → `main` (after alignment)

**"Can I push from Internal Server?"**

Yes! To `internal` branch only, with safety checks.

**"How do I get changes from the other environment?"**

```bash
git pull origin develop   # Get External changes
git pull origin internal  # Get Internal changes
```

---

## 📋 Typical Scenarios

### Scenario 1: Simple Development (No Internal Changes)

```bash
# External PC
git checkout develop
# ... develop features ...
git push origin develop

# Promote to main
git checkout main
git merge develop
git push origin main

# Internal Server
git checkout main
git pull origin main  # Deploy
```

### Scenario 2: Internal Found & Fixed Issue

```bash
# Internal Server
git checkout develop
git pull origin develop
# Test... found bug!

git checkout internal
# Fix bug
git push origin internal

# External PC
git checkout develop
git pull origin internal
git merge internal  # Get the fix
git push origin develop
```

### Scenario 3: Both Have Changes

```bash
# External PC (alignment)
git checkout develop
git pull origin develop
git pull origin internal
git merge internal
# Resolve conflicts if any
git checkout main
git merge develop
git push origin main

# Internal Server (deploy)
git pull origin main
```

---

## 🛡️ Safety

**External PC:**
- ✅ Safe to push code
- ✅ Can commit freely
- ⚠️ Still don't commit .env files

**Internal Server:**
- ⚠️ Check before EVERY push
- ❌ Never push .env files
- ❌ Never push sensitive data
- ✅ Only push code fixes to `internal` branch

**See:** [safety-checklist.md](safety-checklist.md)

---

## 🆘 Quick Help

**"I have merge conflicts"**  
→ [conflict-resolution.md](conflict-resolution.md)

**"How do I align branches?"**  
→ [merge-alignment-guide.md](merge-alignment-guide.md)

**"What can Internal Server push?"**  
→ [internal-workflow.md](internal-workflow.md#-safe-to-push)

**"I'm starting from scratch"**  
→ [setup-instructions.md](setup-instructions.md)

---

**Version:** 2.0 (Dual-Track)  
**Last Updated:** 2025-10-18
