# Quick Reference Card

**Print and keep handy!**

---

## 🌿 Branch Structure (Dual-Track)

```
main ← Production (protected)
  ↑
  ├── develop ← External PC
  │     ↑
  │     └── feature/*
  │
  └── internal ← Internal Server
```

---

## ⚡ External PC Commands

### Daily Development
```bash
# Start
git checkout develop
git pull origin develop
git checkout -b feature/name

# Work
git add .
git commit -m "Description"
git push origin feature/name

# Merge
git checkout develop
git merge feature/name
git push origin develop
```

### Promote to Production
```bash
# Simple (no internal changes)
git checkout main
git merge develop
git push origin main

# With alignment (internal has changes)
git checkout develop
git pull origin internal
git merge internal
git checkout main
git merge develop
git push origin main
```

---

## ⚡ Internal Server Commands

### Test Development
```bash
git checkout develop
git pull origin develop
```

### Make Fixes
```bash
git checkout internal
# ... fix ...
# SAFETY CHECK!
git add <files>
git commit -m "Fix: description"
git push origin internal
```

### Deploy Production
```bash
git checkout main
git pull origin main
```

---

## 🚨 Pre-Push Safety (Internal)

- [ ] `git status` - Check files
- [ ] `git diff` - Review changes  
- [ ] No `.env` files
- [ ] No sensitive data
- [ ] Only code fixes

---

## 🆘 Emergency

```bash
# Undo last commit
git reset --soft HEAD~1

# Discard changes
git checkout -- <file>

# Abort merge
git merge --abort

# Rollback
git checkout HEAD~1
```

---

## 📁 Safety Rules

### NEVER Commit:
❌ `.env`  
❌ `*.db`  
❌ Passwords/keys  
❌ User data  

### ALWAYS:
✅ Check before push  
✅ Test after merge  
✅ Clear messages  

---

## 🔄 Typical Flow

```
External: feature → develop → GitHub
Internal: pull develop → test
Internal: fix → internal → GitHub
External: align → main → GitHub
Internal: pull main → deploy
```

---

## 🎯 Branch Rules

**main:** Production only, merge after alignment  
**develop:** External PC work  
**internal:** Internal Server fixes  
**feature/*:** Daily development  

---

## ⚡ Quick Status

```bash
git status          # What changed?
git branch          # Current branch?
git log -5          # Recent commits?
git diff            # Show changes?
```

---

**Full Docs:** `github-workflow/README.md`
