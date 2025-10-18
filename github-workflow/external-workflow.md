# External PC Workflow

**Environment:** Your personal development PC  
**Safety Level:** High (safe to push code)  
**Primary Role:** Development, feature creation, merge & alignment

---

## 🚀 Daily Development

### Start New Feature

```bash
git checkout develop
git pull origin develop
git checkout -b feature/descriptive-name

# Examples:
# feature/fix-login-bug
# feature/add-chat-export
# feature/improve-performance
```

### Work and Commit

```bash
# Make changes
# ... edit files ...

# Check changes
git status
git diff

# Commit often (small commits)
git add .
git commit -m "Clear description"

# Examples:
# "Fix: Azure AD token validation"
# "Add: Chat export to PDF feature"
# "Improve: Database query performance"
```

### Push Feature Branch

```bash
git push origin feature/descriptive-name

# First time? Add -u flag
git push -u origin feature/descriptive-name
```

### Merge to Develop

```bash
git checkout develop
git pull origin develop
git merge feature/descriptive-name

# If conflicts: See conflict-resolution.md
# If clean: push
git push origin develop

# Clean up
git branch -d feature/descriptive-name
```

---

## 📦 Promote to Production

### Option A: Only Develop Has Changes

```bash
# Simple path - no internal changes to merge
git checkout main
git pull origin main
git merge develop
git push origin main
```

### Option B: Both Develop & Internal Have Changes

```bash
# 1. Get both branches
git checkout develop
git pull origin develop
git checkout internal
git pull origin internal

# 2. Merge internal into develop
git checkout develop
git merge internal

# 3. Resolve conflicts if any (see merge-alignment-guide.md)

# 4. Test merged code
# ... test locally ...

# 5. Promote to main
git checkout main
git pull origin main
git merge develop
git push origin main

# 6. Notify Internal Server to deploy
```

**See [merge-alignment-guide.md](merge-alignment-guide.md) for detailed process**

---

## 🐛 Responding to Internal Server Issues

### Internal Reports Bug

```bash
# Pull their changes
git checkout internal
git pull origin internal

# Review what they found/fixed
git log -5
git diff main..internal

# Merge to develop
git checkout develop
git merge internal

# Continue development with fix included
```

---

## 🔄 Multiple Features

```bash
# Work on multiple features in parallel
git checkout -b feature/auth-fix
# ... work ...
git push origin feature/auth-fix

git checkout develop
git checkout -b feature/chat-export
# ... work ...
git push origin feature/chat-export

# Merge independently
git checkout develop
git merge feature/auth-fix
git push origin develop

git merge feature/chat-export
git push origin develop
```

---

## ⚡ Quick Commands

```bash
# Status & Info
git branch                  # Current branch
git status                  # What's changed
git diff                    # Show changes
git log --oneline -10       # Recent commits

# Branch Operations
git checkout <branch>       # Switch branch
git checkout -b <name>      # Create & switch
git branch -d <name>        # Delete branch

# Sync
git pull origin <branch>    # Get updates
git push origin <branch>    # Send updates

# Merge
git merge <branch>          # Merge branch into current
git merge --abort           # Cancel merge

# Undo
git checkout -- <file>      # Discard local changes
git reset --soft HEAD~1     # Undo last commit (keep changes)
```

---

## 📋 Daily Routine

### Morning

```bash
git checkout develop
git pull origin develop
git pull origin main  # See production updates
```

### During Day

```bash
# Start feature
git checkout -b feature/task
# ... work ...
git add .
git commit -m "Description"
git push origin feature/task

# Merge when done
git checkout develop
git merge feature/task
git push origin develop
```

### End of Sprint

```bash
# Check if Internal has changes
git fetch origin
git branch -r | grep internal

# If internal branch exists:
# Follow "Promote to Production - Option B"

# If no internal branch:
git checkout main
git merge develop
git push origin main
```

---

## 🎯 Best Practices

**Commits:**
- Small, focused commits
- Clear messages
- Test before committing

**Branches:**
- One feature per branch
- Short-lived (hours/days)
- Delete after merge

**Merging:**
- Pull before push
- Test after merge
- Check for conflicts

**Alignment:**
- Review internal changes before merging
- Test merged code
- Communicate with Internal Server

---

## 🚨 What NOT to Do

❌ Never push directly to `main`  
❌ Never commit `.env` files  
❌ Never force push (`git push -f`) without good reason  
❌ Never merge without testing  
❌ Never commit large files (databases, videos)  
❌ Never ignore merge conflicts (resolve them)

---

## 🔍 Checking Internal Changes

```bash
# See if internal branch exists
git fetch origin
git branch -r | grep internal

# If exists, see what changed
git diff develop..origin/internal

# See commits
git log develop..origin/internal --oneline

# Decide if needs review before merging
```

---

## 🆘 Troubleshooting

### "Cannot push to main"

```bash
# Correct! Never push to main directly
# Use: develop → main merge instead
git checkout main
git merge develop
git push origin main
```

### "Conflicts when merging"

```bash
# See conflict-resolution.md
# Quick fix:
git merge <branch>
# Edit conflicted files
# Remove <<<, ===, >>> markers
git add <resolved-files>
git commit
```

### "Lost my changes"

```bash
# See recent commits
git reflog

# Recover lost commit
git checkout <commit-hash>
```

### "Wrong branch"

```bash
# Move uncommitted changes to correct branch
git stash
git checkout correct-branch
git stash pop
```

---

## 🎓 Workflow Summary

```
1. Feature Development:
   develop → feature/* → develop

2. Testing:
   develop → Internal Server (pull & test)

3. Internal Fixes (if needed):
   Internal Server → internal branch

4. Alignment:
   develop + internal → review → merge

5. Production:
   merged develop → main

6. Deploy:
   main → Internal Server (pull & deploy)
```

---

## 📊 Branch Overview

```bash
# See all branches and their status
git branch -a

# Output example:
# * develop                    (current)
#   main
#   feature/auth-fix
#   remotes/origin/develop
#   remotes/origin/internal
#   remotes/origin/main
```

---

**Remember:** You're the integration point. Review both `develop` (your work) and `internal` (production fixes) before promoting to `main`.
