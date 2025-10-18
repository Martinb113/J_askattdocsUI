# Safety Checklist

## 🔒 Before ANY Git Push

### 1. Review What You're Pushing

```bash
# See what files are changed
git status

# See the actual changes
git diff

# See what's staged for commit
git diff --staged
```

### 2. Sensitive Data Check

**NEVER commit these:**
- [ ] `.env` files
- [ ] `.env.local`, `.env.production`, etc.
- [ ] Database files (`.db`, `.sqlite`)
- [ ] Backup files (`.bak`, `.backup`)
- [ ] Log files with real data
- [ ] Configuration files with passwords/keys
- [ ] Private keys (`.pem`, `.key`)
- [ ] API keys or tokens
- [ ] Internal URLs or IP addresses
- [ ] User data or credentials
- [ ] Company-specific secrets

### 3. Code Review

- [ ] Does code contain hardcoded passwords?
- [ ] Does code contain internal IP addresses?
- [ ] Does code contain company-specific business logic (if proprietary)?
- [ ] Are there any TODO comments with sensitive info?
- [ ] Are there any debug print statements with data?

### 4. File Size Check

```bash
# Check file sizes (large files might be binaries/databases)
git diff --stat
```

- [ ] All files are code/text files (not binaries)
- [ ] No files over 1MB (except intentional assets)

---

## 🌿 Branch Safety

### Before Pushing to Develop

- [ ] Are you on the correct branch? (`git branch`)
- [ ] Have you tested the code locally?
- [ ] Did you pull latest changes first? (`git pull origin develop`)

### Before Merging to Main

- [ ] Has code been tested in `develop`?
- [ ] Are all tests passing?
- [ ] Have you reviewed all changes? (`git diff develop..main`)
- [ ] Is this a stable version ready for production?

---

## 🏢 Internal Server Special Checks

### Before ANY push from Internal Server:

- [ ] Am I pushing ONLY issue documentation?
- [ ] No code changes included?
- [ ] No .env or config files?
- [ ] File contains no sensitive data?
- [ ] Have I reviewed the file content line by line?

**If ANY answer is NO or uncertain: DO NOT PUSH**

---

## ✅ Safe Push Checklist

```bash
# 1. Check current branch
git branch
# ✓ Correct branch?

# 2. Review changes
git status
git diff
# ✓ Only files you intended?
# ✓ No sensitive data?

# 3. Check staged files
git diff --staged
# ✓ Correct files staged?

# 4. Verify .gitignore is working
# .env should NOT appear in git status
git status | grep -i env
# ✓ Shows nothing?

# 5. If all checks pass:
git commit -m "Clear, descriptive message"
git push origin <branch-name>
```

---

## 🚨 Emergency: Pushed Sensitive Data

If you accidentally pushed sensitive data:

### Immediate Actions:

1. **DO NOT PANIC** (but act quickly)

2. **Rotate/Change the exposed secrets immediately**
   - Change passwords
   - Regenerate API keys
   - Update credentials everywhere

3. **Remove from Git history** (complex - research carefully)
   ```bash
   # This is dangerous - back up first
   # Consider professional help for this
   ```

4. **Contact GitHub support** if public repository

5. **Document the incident** for security team

---

## 🛡️ Prevention Tools

### 1. Enhanced .gitignore

Ensure these patterns in `.gitignore`:

```
# Environment files
.env
.env.*
!.env.example
!.env.*.example

# Database files
*.db
*.sqlite
*.sql

# Logs
*.log

# Backups
*.bak
*.backup
*.old

# OS files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
```

### 2. Pre-commit Hook (Optional)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Block commit if .env file is staged

if git diff --cached --name-only | grep -q "^\.env$"; then
    echo "ERROR: Attempted to commit .env file!"
    echo "This file contains sensitive data and should not be committed."
    exit 1
fi

echo "✓ Pre-commit checks passed"
exit 0
```

### 3. Regular Audits

Weekly/Monthly:
```bash
# Check for accidentally tracked sensitive files
git ls-files | grep -E '\.(env|key|pem|secret)$'

# Should return nothing
```

---

## 📋 Quick Decision Tree

**About to push? Ask:**

1. **Am I on the right branch?**
   - No → Switch branch
   - Yes → Continue

2. **Have I reviewed all changes?**
   - No → Review with `git diff`
   - Yes → Continue

3. **Any sensitive data in changes?**
   - Yes → Remove it, DO NOT PUSH
   - No → Continue

4. **Am I pushing from Internal Server?**
   - Yes → Only push if issue documentation (recheck everything)
   - No → Safe to push (if other checks pass)

5. **All checks pass?**
   - Yes → Push
   - No → Fix issues first

---

**Remember:** It takes 5 seconds to check, but hours/days to fix a leak. Always verify before pushing!

