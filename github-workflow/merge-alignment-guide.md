# Merge & Alignment Guide

**Purpose:** Align `develop` and `internal` branches before promoting to `main`

**When:** Both branches have changes that need to go to production

**Who:** External PC (review and merge role)

---

## 🎯 Quick Overview

```
develop (External changes)  ──┐
                              ├──→ Review → Align → main
internal (Internal changes) ──┘
```

**Goal:** Merge both tracks safely without breaking production

---

## 🔄 Complete Merge Process

### Step 1: Update Local Branches

```bash
# Get latest from both branches
git checkout develop
git pull origin develop

git checkout internal
git pull origin internal

# Check if internal branch exists
git branch -a | grep internal
# If not found, skip to "No Internal Changes" section
```

### Step 2: Review Both Branches

```bash
# Compare what's different between branches
git diff develop..internal

# See commit history
git log develop..internal --oneline
git log internal..develop --oneline

# Understand what each branch changed
```

### Step 3: Merge Internal into Develop

```bash
git checkout develop
git merge internal

# Two outcomes:
```

#### Outcome A: No Conflicts ✅

```bash
# If merge succeeds automatically:
Auto-merging <files>
Merge made by the 'recursive' strategy.

# Merged! Proceed to testing
```

#### Outcome B: Conflicts ⚠️

```bash
# If conflicts occur:
Auto-merging backend/app/api/v1/auth.py
CONFLICT (content): Merge conflict in backend/app/api/v1/auth.py

# See conflict-resolution.md for detailed guide
```

### Step 4: Resolve Conflicts (if any)

```bash
# Open conflicted files
# Look for conflict markers:
<<<<<<< HEAD
  Code from develop
=======
  Code from internal
>>>>>>> internal

# Edit file to resolve:
# - Keep develop version, OR
# - Keep internal version, OR
# - Combine both (most common)

# Remove conflict markers (<<<<, ====, >>>>)

# Mark as resolved
git add <resolved-file>
```

### Step 5: Test Merged Code

```bash
# CRITICAL: Test before promoting to main

# Run linter
ruff check backend/

# Run tests
pytest tests/

# Start application locally
# Test key functionality

# If tests fail: Fix issues, commit fixes
# If tests pass: Proceed to promote
```

### Step 6: Promote to Main

```bash
git checkout main
git pull origin main

# Merge the aligned develop branch
git merge develop

# Push to production
git push origin main
```

### Step 7: Clean Up (Optional)

```bash
# Delete old internal branch (start fresh next time)
git push origin --delete internal
git branch -d internal

# Or keep it and reset to match main
git checkout internal
git reset --hard main
git push origin internal --force
```

---

## 🚀 Quick Merge (No Conflicts Expected)

```bash
# Fast path when changes don't overlap
git checkout develop
git pull origin develop
git pull origin internal
git merge internal
git checkout main
git merge develop
git push origin main
```

---

## 🔍 Scenarios

### Scenario 1: Only Develop Has Changes

```bash
# No internal branch exists or no changes
git checkout main
git merge develop
git push origin main

# Simple - no alignment needed
```

### Scenario 2: Only Internal Has Changes

```bash
# No develop changes, only internal fixes
git checkout internal
git pull origin internal

git checkout main
git merge internal
git push origin main
```

### Scenario 3: Both Have Changes (Common)

```bash
# Follow full merge process above
# Key: merge internal → develop first
# Then: develop → main
# This keeps develop as integration point
```

### Scenario 4: Conflicts in Same Files

```bash
# Both branches modified same lines
git checkout develop
git merge internal
# CONFLICT!

# Resolve conflicts manually
# Understand both changes
# Decide which to keep or combine
# Test thoroughly
# Then promote to main
```

---

## 🛡️ Safety Checks

### Before Merging to Main

- [ ] Both `develop` and `internal` pulled
- [ ] Conflicts resolved (if any)
- [ ] Code tested locally
- [ ] Linter passes
- [ ] Tests pass (if you have them)
- [ ] Application starts without errors
- [ ] Key features work

### After Pushing to Main

- [ ] Notify Internal Server
- [ ] Internal Server pulls and tests
- [ ] Monitor production logs
- [ ] Verify deployment successful

---

## 📋 Conflict Resolution Quick Guide

### Simple Conflict (Choose One)

```python
<<<<<<< HEAD
user = validate_token_v1(token)
=======
user = validate_token_v2(token)
>>>>>>> internal

# Resolution: Keep v2 (newer)
user = validate_token_v2(token)
```

### Complex Conflict (Combine Both)

```python
<<<<<<< HEAD
def process():
    clean_data()
    return result
=======
def process():
    validate_input()
    return result
>>>>>>> internal

# Resolution: Need both
def process():
    validate_input()
    clean_data()
    return result
```

### When in Doubt

1. Understand why each change was made
2. Check commit messages for context
3. Test both versions locally
4. Ask yourself: Can both changes coexist?
5. If unsure: Keep internal version (it's production-tested)

---

## ⚡ Emergency: Need to Abort

```bash
# If merge goes wrong, abort it
git merge --abort

# Back to state before merge
# Try again or ask for help
```

---

## 🎯 Best Practices

1. **Merge regularly** - Don't let branches diverge too much
2. **Small changes** - Easier to merge
3. **Clear commits** - Understand what changed and why
4. **Test before main** - Always test merged code
5. **Communicate** - Know what Internal Server changed

---

## 📊 Typical Timeline

```
Week 1:
  Day 1-3: External PC → develop (features)
  Day 4-5: Internal Server → internal (production fixes)

Week 2:
  Day 1: External PC → Merge & align both branches
  Day 2: External PC → Test merged code
  Day 3: External PC → Promote to main
  Day 3: Internal Server → Pull main, deploy

Repeat...
```

---

## 💡 Pro Tips

**Keep Internal Changes Minimal:**
- Only production-specific fixes
- Small, focused changes
- Easier to merge

**Merge Direction Matters:**
```bash
# Correct: internal → develop → main
git checkout develop
git merge internal

# Avoid: develop → internal (confuses ownership)
```

**When to Skip Alignment:**
- Only one branch has changes
- Changes are in completely different files
- Just pull and merge directly to main

**When to Be Careful:**
- Both modified same file
- Changes touch same function
- Configuration changes on both sides

---

**Remember:** This is a review and alignment step. Take time to understand both sets of changes before merging to production.

