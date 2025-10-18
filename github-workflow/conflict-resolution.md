# Conflict Resolution Guide

## 🤔 What Are Merge Conflicts?

Merge conflicts occur when:
- Same file was changed in two different branches
- Git can't automatically decide which changes to keep

**Don't panic!** Conflicts are normal and easy to fix.

---

## 🔍 Identifying Conflicts

### When merging:

```bash
git merge feature/some-branch

# If conflict occurs:
Auto-merging backend/app/api/v1/auth.py
CONFLICT (content): Merge conflict in backend/app/api/v1/auth.py
Automatic merge failed; fix conflicts and then commit the result.
```

### Check conflict status:

```bash
# See which files have conflicts
git status

# Shows:
# Unmerged paths:
#   both modified:   backend/app/api/v1/auth.py
```

---

## 🛠️ Resolving Conflicts

### Step 1: Open the conflicted file

Git marks conflicts with special markers:

```python
def authenticate_user(token: str):
<<<<<<< HEAD
    # Your current branch version
    user = validate_azure_token(token)
    return user
=======
    # Incoming branch version
    user = validate_token_v2(token)
    if not user:
        raise AuthenticationError()
    return user
>>>>>>> feature/auth-fix
```

### Step 2: Understand the markers

```
<<<<<<< HEAD
  Your current code (develop branch)
=======
  Incoming code (feature branch)
>>>>>>> feature/branch-name
```

### Step 3: Decide what to keep

**Option A:** Keep current version (HEAD)
```python
def authenticate_user(token: str):
    user = validate_azure_token(token)
    return user
```

**Option B:** Keep incoming version
```python
def authenticate_user(token: str):
    user = validate_token_v2(token)
    if not user:
        raise AuthenticationError()
    return user
```

**Option C:** Combine both (most common)
```python
def authenticate_user(token: str):
    # Use new validation method with error handling
    user = validate_token_v2(token)
    if not user:
        raise AuthenticationError()
    return user
```

### Step 4: Remove conflict markers

Delete the `<<<<<<<`, `=======`, and `>>>>>>>` lines:

```python
# Final resolved version:
def authenticate_user(token: str):
    user = validate_token_v2(token)
    if not user:
        raise AuthenticationError()
    return user
```

### Step 5: Mark as resolved

```bash
# Add the resolved file
git add backend/app/api/v1/auth.py

# Check status
git status

# Should show:
# All conflicts fixed: run "git commit" to complete the merge
```

### Step 6: Complete the merge

```bash
# Commit the resolution
git commit -m "Resolved merge conflict in auth.py"

# Or just:
git commit  # Opens editor with pre-filled message

# Push if needed
git push origin develop
```

---

## 🎯 Conflict Prevention Strategies

### 1. Pull Before Starting Work

```bash
# Always get latest before creating feature branch
git checkout develop
git pull origin develop
git checkout -b feature/new-thing
```

### 2. Merge Frequently

```bash
# While working on feature branch, periodically:
git checkout feature/your-branch
git pull origin develop
git merge develop

# This keeps your branch up to date
```

### 3. Small, Focused Changes

- Work on one feature at a time
- Keep feature branches short-lived (hours/days, not weeks)
- Commit and merge frequently

### 4. Communicate

- If working with others, discuss who's working on what
- For solo work: Finish one feature before starting another

---

## 🔧 Advanced Conflict Resolution

### Abort a Merge

If conflicts are too complex, start over:

```bash
# Cancel the merge
git merge --abort

# You're back to state before merge attempt
```

### Use Visual Merge Tools

```bash
# Configure VS Code as merge tool
git config merge.tool vscode
git config mergetool.vscode.cmd 'code --wait $MERGED'

# Then when conflicts occur:
git mergetool
```

### View Conflict History

```bash
# See what changed in both branches
git log --merge

# See detailed conflict info
git diff
```

---

## 📋 Common Conflict Scenarios

### Scenario 1: Simple Text Change

**Conflict:**
```python
<<<<<<< HEAD
SECRET_KEY = "old-key-value"
=======
SECRET_KEY = "new-key-value"
>>>>>>> feature/update-config
```

**Resolution:** Keep the newer value
```python
SECRET_KEY = "new-key-value"
```

---

### Scenario 2: Function Modified Differently

**Conflict:**
```python
<<<<<<< HEAD
def process_message(msg: str):
    cleaned = msg.strip()
    return cleaned
=======
def process_message(msg: str):
    cleaned = msg.strip().lower()
    validated = validate_message(cleaned)
    return validated
>>>>>>> feature/message-validation
```

**Resolution:** Combine improvements
```python
def process_message(msg: str):
    cleaned = msg.strip().lower()
    validated = validate_message(cleaned)
    return validated
```

---

### Scenario 3: Import Conflicts

**Conflict:**
```python
<<<<<<< HEAD
from app.services import auth, chat
=======
from app.services import auth, conversation
>>>>>>> feature/rename-chat
```

**Resolution:** Include all imports needed
```python
from app.services import auth, chat, conversation
```

---

## 🚨 When to Ask for Help

Consider getting assistance if:
- Conflicts affect more than 5 files
- You're unsure which version is correct
- Conflicts involve complex logic or algorithms
- The merge conflict is in generated code (migrations, etc.)

---

## ✅ Post-Resolution Checklist

After resolving conflicts:

- [ ] All conflict markers removed
- [ ] Code still makes logical sense
- [ ] Imports are correct
- [ ] Run linter: `ruff check .`
- [ ] Run tests (if you have them)
- [ ] Test the application locally
- [ ] Commit and push

```bash
# Quick verification
git status  # Should show no conflicts
git diff    # Review your resolution

# If looks good:
git add .
git commit -m "Resolved conflicts in [file names]"
git push origin <branch-name>
```

---

## 💡 Pro Tips

1. **Read both versions carefully** - Sometimes both changes are needed
2. **Test after resolving** - Make sure code still works
3. **Don't rush** - Take time to understand what each version does
4. **Ask yourself**: "Why was this changed in both places?"
5. **Keep both features** when possible, unless they're mutually exclusive

---

**Remember:** Conflicts are Git's way of asking "Both versions changed this - which one should I keep?" You're just answering that question.

