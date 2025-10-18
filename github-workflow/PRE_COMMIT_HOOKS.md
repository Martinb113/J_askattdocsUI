# Pre-Commit Hooks Setup

**Purpose**: Automatically prevent sensitive data from being committed  
**Security Level**: Second line of defense (after manual review)

---

## 🎯 What Are Pre-Commit Hooks?

Pre-commit hooks are scripts that run automatically **before** every Git commit. They can:
- ✅ Check for sensitive data patterns
- ✅ Block commits containing passwords/keys
- ✅ Enforce code quality standards
- ✅ Prevent common mistakes

**Think of it as**: An automated security guard that reviews your commits.

---

## 🚀 Quick Setup (Windows)

### **Step 1: Create Hook Script**

```powershell
# Navigate to your repository
cd C:\Users\admin\Documents\AI_projects\j_askdocs

# Create the hooks directory (if needed)
mkdir .git\hooks -Force

# Create pre-commit hook
notepad .git\hooks\pre-commit
```

### **Step 2: Copy This Script**

Paste this into the `pre-commit` file (no file extension!):

```bash
#!/bin/sh
# Pre-commit hook to prevent sensitive data from being committed
#
# This hook checks for common patterns that indicate sensitive data
# If found, it blocks the commit and shows a warning

echo "🔍 Running security checks..."

# Define patterns to search for
PATTERNS=(
    "password\s*=\s*['\"][^'\"]*['\"]"
    "PASSWORD\s*=\s*['\"][^'\"]*['\"]"
    "api[_-]?key\s*=\s*['\"][^'\"]*['\"]"
    "API[_-]?KEY\s*=\s*['\"][^'\"]*['\"]"
    "secret[_-]?key\s*=\s*['\"][^'\"]*['\"]"
    "SECRET[_-]?KEY\s*=\s*['\"][^'\"]*['\"]"
    "token\s*=\s*['\"][^'\"]*['\"]"
    "TOKEN\s*=\s*['\"][^'\"]*['\"]"
    "postgresql://[^'\"\s]*:[^'\"\s]*@"
    "mysql://[^'\"\s]*:[^'\"\s]*@"
    "mongodb://[^'\"\s]*:[^'\"\s]*@"
)

# Files that should never be committed
FORBIDDEN_FILES=(
    ".env"
    ".env.local"
    ".env.production"
    "*.db"
    "*.sqlite"
    "*.sqlite3"
    "credentials.json"
    "secrets.yaml"
)

# Check for forbidden files
echo "  Checking for forbidden files..."
for pattern in "${FORBIDDEN_FILES[@]}"; do
    if git diff --cached --name-only | grep -qE "$pattern"; then
        echo "❌ ERROR: Attempting to commit forbidden file matching: $pattern"
        echo ""
        echo "   Files found:"
        git diff --cached --name-only | grep -E "$pattern" | sed 's/^/     - /'
        echo ""
        echo "   These files should NEVER be committed!"
        echo "   Add them to .gitignore instead."
        echo ""
        exit 1
    fi
done

# Check for sensitive data patterns in staged changes
echo "  Checking for sensitive data patterns..."
for pattern in "${PATTERNS[@]}"; do
    if git diff --cached | grep -qiE "$pattern"; then
        echo "❌ ERROR: Potential sensitive data detected!"
        echo ""
        echo "   Pattern matched: $pattern"
        echo ""
        echo "   Lines that matched:"
        git diff --cached | grep -iE "$pattern" | head -5 | sed 's/^/     /'
        echo ""
        echo "   ⚠️ If this is actual sensitive data:"
        echo "      1. Remove it from code"
        echo "      2. Add to .env file instead"
        echo "      3. Use environment variables"
        echo ""
        echo "   ⚠️ If this is a false positive (e.g., example code):"
        echo "      You can skip this hook with: git commit --no-verify"
        echo "      (But be VERY careful!)"
        echo ""
        exit 1
    fi
done

# Special check for database URLs
echo "  Checking for database connection strings..."
if git diff --cached | grep -qiE "(postgresql|mysql|mongodb)://[^@'\"\s]+:[^@'\"\s]+@"; then
    echo "❌ ERROR: Database connection string with credentials detected!"
    echo ""
    echo "   Database URLs with passwords should be in .env files, not in code!"
    echo ""
    echo "   Use environment variables instead:"
    echo "     # In .env file:"
    echo "     DATABASE_URL=postgresql://user:pass@host:5432/db"
    echo ""
    echo "     # In your code:"
    echo "     from app.config import settings"
    echo "     db_url = settings.database_url"
    echo ""
    exit 1
fi

# Check for internal IP addresses
echo "  Checking for internal IP addresses..."
if git diff --cached | grep -qE "(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)[0-9]+\.[0-9]+"; then
    echo "⚠️ WARNING: Internal IP address detected!"
    echo ""
    echo "   Found IP addresses that look like internal network addresses."
    echo "   Make sure you're not exposing internal infrastructure."
    echo ""
    git diff --cached | grep -E "(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)[0-9]+\.[0-9]+" | head -3 | sed 's/^/     /'
    echo ""
    echo "   If this is intentional, you can continue with: git commit --no-verify"
    echo "   But please review carefully!"
    echo ""
    read -p "   Continue anyway? (y/N): " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "   Commit cancelled."
        exit 1
    fi
fi

echo "✅ Security checks passed!"
echo ""
exit 0
```

### **Step 3: Make Script Executable**

```powershell
# On Windows with Git Bash
"C:\Program Files\Git\bin\bash.exe" -c "chmod +x .git/hooks/pre-commit"

# Or use Git Bash directly
# Right-click in folder → "Git Bash Here"
chmod +x .git/hooks/pre-commit
```

---

## 🧪 Test Your Hook

### **Test 1: Try to commit a .env file** (Should FAIL ❌)

```powershell
# Create a test .env file
echo "SECRET_KEY=test123" > test.env

# Try to commit it
git add test.env
git commit -m "Test: Adding env file"

# Expected result:
# ❌ ERROR: Attempting to commit forbidden file matching: .env
# The hook should block this commit!

# Clean up
git reset HEAD test.env
del test.env
```

### **Test 2: Try to commit code with password** (Should FAIL ❌)

```powershell
# Create a test file with password
echo "password = 'my_secret_pass'" > test_password.py

# Try to commit it
git add test_password.py
git commit -m "Test: Adding password"

# Expected result:
# ❌ ERROR: Potential sensitive data detected!
# The hook should block this commit!

# Clean up
git reset HEAD test_password.py
del test_password.py
```

### **Test 3: Normal commit** (Should PASS ✅)

```powershell
# Create a normal code file
echo "def hello(): return 'world'" > test_hello.py

# Commit it
git add test_hello.py
git commit -m "Test: Normal code"

# Expected result:
# ✅ Security checks passed!
# Commit should succeed

# Clean up
git rm test_hello.py
git commit -m "Clean up test file"
```

---

## 🔧 Advanced Configuration

### **Customize Patterns**

Edit `.git/hooks/pre-commit` to add/remove patterns:

```bash
# Add custom patterns for your environment
PATTERNS=(
    # ... existing patterns ...
    
    # Add your company-specific patterns
    "company[_-]?secret"
    "internal[_-]?api[_-]?key"
    "prod[_-]?password"
)

# Add custom forbidden files
FORBIDDEN_FILES=(
    # ... existing patterns ...
    
    # Add your specific files
    "company-config.json"
    "production.yml"
)
```

### **Adjust Sensitivity**

**More Strict** (Catch more potential issues):
```bash
# Check for any string that looks like a secret
PATTERNS+=(
    "[a-zA-Z0-9]{32,}"  # Long random strings
    "sk_[a-zA-Z0-9]+"   # Stripe-style keys
    "ghp_[a-zA-Z0-9]+"  # GitHub personal tokens
)
```

**Less Strict** (Allow more, but riskier):
```bash
# Only check for very obvious secrets
PATTERNS=(
    "password\s*=\s*['\"][^'\"]{8,}['\"]"  # Only long passwords
    "api_key\s*=\s*['\"]sk_[^'\"]*['\"]"   # Only keys starting with sk_
)
```

---

## 🚫 Bypassing the Hook (Emergency Only!)

**When you might need to bypass:**
- ✅ False positive (example code, documentation)
- ✅ Intentional commit of template files
- ❌ NEVER to commit actual sensitive data!

**How to bypass:**
```powershell
# Skip pre-commit hook for this commit only
git commit --no-verify -m "Your message"

# Or short form
git commit -n -m "Your message"
```

⚠️ **WARNING**: Only use `--no-verify` if you're absolutely certain the commit is safe!

---

## 📋 Maintenance

### **Updating the Hook**

```powershell
# Edit the hook script
notepad .git\hooks\pre-commit

# Test it
# (run the tests from "Test Your Hook" section)

# No need to commit - hooks are local to your repository
```

### **Sharing Hooks with Team**

Git hooks in `.git/hooks/` are NOT committed to the repository. To share:

**Option 1: Manual setup** (What we're doing)
- Document in this file
- Each developer sets up manually

**Option 2: Automated setup script**

Create `scripts/setup-hooks.sh`:
```bash
#!/bin/bash
# Setup Git hooks for the repository

echo "Setting up Git hooks..."

# Copy pre-commit hook
cp scripts/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Hooks installed!"
```

Then each developer runs:
```powershell
bash scripts/setup-hooks.sh
```

### **Disable Hook Temporarily**

```powershell
# Rename to disable
mv .git\hooks\pre-commit .git\hooks\pre-commit.disabled

# Rename back to enable
mv .git\hooks\pre-commit.disabled .git\hooks\pre-commit
```

---

## 🔍 Hook Limitations

### **What Hooks CAN Do**
- ✅ Check patterns in staged files
- ✅ Block commits with obvious secrets
- ✅ Prevent common mistakes
- ✅ Provide warnings

### **What Hooks CANNOT Do**
- ❌ Check files not staged for commit
- ❌ Detect all possible sensitive data (false negatives)
- ❌ Read your mind (might have false positives)
- ❌ Protect against `--no-verify`
- ❌ Run on other people's machines (local only)

### **Important Reminders**

1. **Hooks are LOCAL** - They only exist on your machine
2. **Hooks can be bypassed** - Don't rely on them 100%
3. **Manual review still needed** - Hooks complement, don't replace, manual checks
4. **False positives happen** - Sometimes legitimate code triggers warnings
5. **Keep updated** - Add patterns as you discover new risks

---

## 🛡️ Defense in Depth

Pre-commit hooks are just one layer of security:

```
Layer 1: Education & Awareness
   ↓ (You know what not to commit)
Layer 2: .gitignore
   ↓ (Prevents files from being staged)
Layer 3: Pre-commit hooks
   ↓ (Blocks commits with sensitive patterns)
Layer 4: Manual review
   ↓ (You review git diff before push)
Layer 5: Repository scanning
   ↓ (GitHub secret scanning, if enabled)
```

**All layers are important!** Don't skip manual review just because you have a hook.

---

## 📊 Hook Performance

### **How Fast Are Hooks?**

Typical timing:
- Small commit (1-5 files): < 1 second
- Medium commit (10-20 files): 1-2 seconds
- Large commit (50+ files): 3-5 seconds

### **If Hook is Too Slow**

Optimize patterns or limit scope:

```bash
# Only check specific file types
if git diff --cached --name-only | grep -qE '\\.py$'; then
    # Only check Python files
fi

# Only check text files (skip binaries)
git diff --cached --diff-filter=ACM --name-only | while read file; do
    if file "$file" | grep -q text; then
        # Check this file
    fi
done
```

---

## ❓ Troubleshooting

### **Hook doesn't run at all**

**Cause**: File not executable or in wrong location

**Solution**:
```powershell
# Check file exists
ls .git\hooks\pre-commit

# Make executable (Git Bash)
chmod +x .git/hooks/pre-commit

# Verify it's in the right place
# Should be: .git/hooks/pre-commit
# NOT: .git/hooks/pre-commit.sample
```

### **Hook blocks legitimate code**

**Cause**: False positive from pattern matching

**Solutions**:
```powershell
# Option 1: Refactor code to not match pattern
# Instead of: password = "test123"
# Use: test_password = "test123"  # Test fixture

# Option 2: Bypass for this commit
git commit --no-verify -m "Add test fixtures"

# Option 3: Update hook patterns
notepad .git\hooks\pre-commit
# Make patterns more specific
```

### **Hook allows sensitive data through**

**Cause**: Pattern doesn't match the specific format

**Solution**:
```powershell
# Add new pattern to hook
notepad .git\hooks\pre-commit

# Add to PATTERNS array:
PATTERNS+=(
    "your-specific-pattern-here"
)
```

### **Hook shows errors/warnings**

**Cause**: Shell script syntax issues (Windows)

**Solution**:
```powershell
# Make sure you're using Unix line endings
# In VS Code: Click "CRLF" in bottom right → Select "LF"

# Or use dos2unix (if available)
dos2unix .git\hooks\pre-commit

# Or reinstall using Git Bash
bash -c "chmod +x .git/hooks/pre-commit"
```

---

## 🎯 Quick Reference

### **Enable Hook**
```powershell
# Create file: .git\hooks\pre-commit
# Copy script from this document
# Make executable: chmod +x .git/hooks/pre-commit
```

### **Test Hook**
```powershell
# Try to commit a .env file - should fail
echo "test" > test.env
git add test.env
git commit -m "test"
git reset HEAD test.env
del test.env
```

### **Bypass Hook (Emergency)**
```powershell
git commit --no-verify -m "message"
```

### **Disable Hook**
```powershell
mv .git\hooks\pre-commit .git\hooks\pre-commit.disabled
```

### **Re-enable Hook**
```powershell
mv .git\hooks\pre-commit.disabled .git\hooks\pre-commit
```

---

## ✅ Setup Checklist

- [ ] Created `.git\hooks\pre-commit` file
- [ ] Copied hook script into file
- [ ] Made file executable (`chmod +x`)
- [ ] Tested with .env file (should block)
- [ ] Tested with password in code (should block)
- [ ] Tested with normal code (should allow)
- [ ] Customized patterns if needed
- [ ] Documented setup for internal server (if applicable)
- [ ] Understand how to bypass in emergencies
- [ ] Still doing manual review (hook is backup, not replacement)

---

**Remember**: Pre-commit hooks are a helpful safety net, but they don't replace careful manual review. Always use `git diff` and `git status` before committing, especially from the Internal Server!

---

**Next Steps**: See [PRODUCTION_WORKFLOW.md](PRODUCTION_WORKFLOW.md) for advanced workflows when you have real users

