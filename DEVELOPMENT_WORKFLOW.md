# Development Workflow Guide

## ✅ Setup Complete!

Your repository now has a safe development workflow:

```
master (production) ← Protected, stable, working code
  ↑
  └── develop ← Development work happens here
        ↑
        └── feature/* ← Individual feature branches
```

---

## 🚀 Daily Development Workflow

### 1. Starting a New Feature

```powershell
# Make sure you're on develop and have latest changes
git checkout develop
git pull origin develop

# Create a feature branch for your work
git checkout -b feature/your-feature-name

# Examples:
# git checkout -b feature/add-export-functionality
# git checkout -b feature/fix-login-bug
# git checkout -b feature/improve-ui
```

### 2. Working on Your Feature

```powershell
# Make your changes, edit files, etc.

# Check what you've changed
git status

# Stage your changes
git add .

# Commit with a clear message
git commit -m "Add: description of what you did"

# Push to GitHub (first time for this branch)
git push -u origin feature/your-feature-name

# Subsequent pushes
git push origin feature/your-feature-name
```

### 3. Merging Feature to Develop

```powershell
# When feature is complete and tested
git checkout develop
git pull origin develop

# Merge your feature
git merge feature/your-feature-name

# Push develop to GitHub
git push origin develop

# Clean up - delete the feature branch
git branch -d feature/your-feature-name
```

### 4. Promoting to Production (When Ready)

```powershell
# Only do this when develop is stable and tested
git checkout master
git pull origin master

# Merge develop into master
git merge develop

# Push to production
git push origin master
```

---

## 🛡️ Safety Rules

### ✅ SAFE to Do:

- Work on `feature/*` branches
- Push to `develop` branch
- Merge features to `develop`
- Test extensively on `develop`
- Create as many feature branches as you need

### ⚠️ BE CAREFUL:

- Only merge to `master` when code is thoroughly tested
- Test on `develop` first before promoting to `master`
- Pull latest changes before creating new branches

### ❌ DON'T:

- Don't work directly on `master` branch
- Don't commit `.env` files (they're already in `.gitignore`)
- Don't merge untested code to `master`
- Don't force push (`git push -f`) unless absolutely necessary

---

## 📋 Quick Command Reference

```powershell
# See current branch
git branch

# See status
git status

# Switch branches
git checkout develop
git checkout master
git checkout feature/name

# Create new feature branch (from develop)
git checkout develop
git checkout -b feature/new-thing

# Update current branch
git pull origin <branch-name>

# Push current branch
git push origin <branch-name>

# See recent commits
git log --oneline -10

# See what changed
git diff
```

---

## 🔄 Typical Week Example

**Monday:**
```powershell
git checkout develop
git checkout -b feature/add-chat-history
# ... work on feature ...
git add .
git commit -m "Add: chat history feature"
git push origin feature/add-chat-history
```

**Tuesday:**
```powershell
# Continue working
git add .
git commit -m "Add: chat history UI improvements"
git push origin feature/add-chat-history
```

**Wednesday:**
```powershell
# Feature complete, merge to develop
git checkout develop
git merge feature/add-chat-history
git push origin develop
```

**Thursday:**
```powershell
# Start another feature
git checkout -b feature/fix-styling
# ... work ...
git add .
git commit -m "Fix: improve button styling"
git push origin feature/fix-styling

# Merge when done
git checkout develop
git merge feature/fix-styling
git push origin develop
```

**Friday:**
```powershell
# Develop is stable, promote to production
git checkout master
git merge develop
git push origin master

# 🎉 New features in production!
```

---

## 🆘 Emergency Commands

**Undo last commit (keep changes):**
```powershell
git reset --soft HEAD~1
```

**Discard all local changes (WARNING: can't undo):**
```powershell
git checkout -- .
```

**Abort a merge:**
```powershell
git merge --abort
```

**See what changed between branches:**
```powershell
git diff develop..master
```

---

## 🎯 Current Branch Status

Right now you're on: `develop` branch ✓

**Your branches:**
- `master` - Your working production code (protected)
- `develop` - Development branch (you're here now)

**Next step:** Create a feature branch when you're ready to add something new!

```powershell
git checkout -b feature/my-first-feature
```

---

## 💡 Best Practices

1. **Small, frequent commits** - Easier to track and undo if needed
2. **Clear commit messages** - "Add: ", "Fix: ", "Update: ", "Refactor: "
3. **One feature per branch** - Keeps things organized
4. **Test before merging** - Especially before merging to master
5. **Pull before you push** - Avoid conflicts
6. **Delete feature branches after merging** - Keeps repo clean

---

## 📊 Visual Workflow

```
You start here:
    feature/new-thing (create from develop)
          │
          │ work, commit, push
          │
          ↓
       develop (merge feature here, test)
          │
          │ when stable
          │
          ↓
       master (production, always working)
```

---

**Questions?** Refer to the detailed guides in `github-workflow/` directory or check `github-workflow/quick-reference.md`

**Remember:** `develop` is your playground. Break things, try things, experiment! `master` stays safe until you're ready.

