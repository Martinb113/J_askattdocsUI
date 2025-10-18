# Production Workflow (Issue-Driven Development)

**Phase**: Production with Real Users  
**Status**: Future Implementation (NOT YET ACTIVE)  
**Use When**: Application is deployed and serving real company users

---

## ⚠️ IMPORTANT NOTICE

**This workflow is NOT active yet!**

This document describes an advanced workflow for when your application is in production with real users. During current development phase, use the simpler workflow in [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md).

**Activate this workflow when:**
- ✅ Application is deployed on internal server
- ✅ Real company users are actively using the system
- ✅ You're receiving bug reports and feature requests
- ✅ Need structured communication between Internal (production) and External (development)

---

## 🎯 Overview

### **The Problem This Solves**

When the app is in production:
1. Users find bugs on **Internal Server** (production)
2. You need to fix bugs on **External PC** (development)
3. The "never-ending loop" problem: Fix doesn't work → Need more info → Another fix → Still doesn't work → etc.

### **The Solution: Issue-Driven Workflow**

Use **structured issue documentation** as a communication bridge:

```
Internal Server (finds issue)
  ↓
Creates issue-XXX.md (detailed documentation)
  ↓
Pushes ONLY the .md file to GitHub
  ↓
External PC pulls the issue
  ↓
Fixes code based on documentation
  ↓
Pushes fix to GitHub
  ↓
Internal Server pulls and tests
  ↓
Updates issue with test results
  ↓
(Repeat until resolved)
```

---

## 📁 Repository Structure

### **Issue Folder Organization**

```
j_askdocs/
├── issues/
│   ├── _templates/
│   │   ├── issue-template.md
│   │   └── ISSUE_WORKFLOW.md
│   ├── open/
│   │   ├── P1-critical/
│   │   │   └── issue-001-login-broken.md
│   │   ├── P2-high/
│   │   │   └── issue-003-chat-slow.md
│   │   └── P3-normal/
│   │       └── issue-005-ui-typo.md
│   ├── in-progress/
│   │   └── issue-002-auth-error.md
│   └── resolved/
│       └── issue-000-example.md
└── backend/
    └── (application code)
```

### **Priority Levels**

| Priority | Response Time | Description | Examples |
|----------|--------------|-------------|----------|
| P1 - Critical | Immediate | System down, blocking all users | Login broken, server crash |
| P2 - High | Same day | Major feature broken, affecting many users | Chat not working, data loss |
| P3 - Normal | 1-3 days | Minor bugs, single-user issues | UI glitches, typos, small bugs |

---

## 📝 Issue Documentation Template

### **File Naming Convention**

```
issue-[number]-[brief-description].md

Examples:
issue-001-login-azure-ad-fails.md
issue-002-chat-timeout-error.md
issue-003-database-connection-slow.md
```

### **Template Content**

```markdown
# Issue #001: Login with Azure AD Fails

## Metadata
- **Status**: Open / In Progress / Testing / Resolved
- **Priority**: P1 Critical / P2 High / P3 Normal
- **Created**: 2025-10-18 14:30
- **Last Updated**: 2025-10-18 14:30
- **Reporter**: Martin (Internal Server)
- **Assignee**: Martin (External PC)

## Environment
- **Location**: Internal Server
- **Version**: Commit hash or version number
- **Affected Users**: All users / Specific users / Single user

## Problem Description

### What's Happening
Users click "Login with Azure AD" and get redirected correctly, but after authentication they see error: "Invalid token - Audience mismatch"

### Impact
- **Severity**: Critical - No one can log in
- **Workaround**: None
- **Users Affected**: All internal users attempting to log in

## Reproduction Steps

1. Navigate to http://internal-server.company.local:5173
2. Click "Sign In with Azure AD"
3. Enter company credentials: [test-user@company.com]
4. Complete 2FA
5. Get redirected back to application
6. ERROR: "Invalid token - Audience mismatch"

### Reproduction Rate
- Consistent: YES - Happens 100% of the time
- Specific conditions: After any Azure AD login

## Expected Behavior
User should be logged in and redirected to /chat page with valid session.

## Actual Behavior
User sees error message and remains on login page. Session is not created.

## Error Messages & Logs

### Frontend Console
```
ERROR: Authentication failed
  Status: 401 Unauthorized
  Message: "Invalid token - Audience mismatch"
```

### Backend Logs
```
2025-10-18 14:28:45 INFO: Received auth callback from Azure AD
2025-10-18 14:28:45 DEBUG: Token received, length: 1234
2025-10-18 14:28:45 ERROR: Token validation failed
  Error: Audience claim mismatch
  Expected: api://12345678-abcd-efgh-ijkl-mnopqrstuvwx
  Received: api://87654321-zyxw-vuts-rqpo-nmlkjihgfedcba
2025-10-18 14:28:45 INFO: Auth request rejected
```

### Database State
- No user session created
- No entry in auth_tokens table

## Technical Context

### Files Likely Involved
- `backend/app/api/v1/auth.py` - Authentication endpoint
- `backend/app/core/security.py` - Token validation
- `backend/app/services/auth.py` - Azure AD service
- `frontend/src/pages/Login.tsx` - Login UI

### Configuration Related
- `.env` variables: AZURE_AD_TENANT_ID, AZURE_AD_CLIENT_ID
- May be mismatch between Azure AD app registration and .env config

### Recent Changes
- No code changes in last 3 days
- Azure AD configuration was updated yesterday by IT team
- Possible that Azure AD settings changed on company side

## Attempted Solutions (if any)
- ❌ Restarted backend server - Did not help
- ❌ Cleared browser cache - Did not help
- ❌ Tried different browser - Same error

## Sensitive Data Notes

⚠️ **DO NOT include in public commits:**
- Actual Azure AD Tenant ID: [REDACTED]
- Actual Client ID: [REDACTED]
- Internal server URLs: [REDACTED]
- User email addresses: Use test-user@company.com in examples

✅ **Safe to share:**
- Error messages (generic)
- Log patterns (without specific IDs)
- File names and line numbers
- Reproduction steps (anonymized)

## Suggested Investigation Steps
1. Verify Azure AD app registration settings
2. Check if AZURE_AD_CLIENT_ID in .env matches Azure Portal
3. Review token validation logic in security.py
4. Compare development vs production Azure AD configurations

## Testing Checklist

When fix is deployed, test the following:

- [ ] Login with test user account
- [ ] Login with admin account
- [ ] Verify token expiration works (wait or mock)
- [ ] Check session persistence after browser close
- [ ] Verify logout clears session
- [ ] Test with different user roles

## Communication Log

### 2025-10-18 14:30 - Initial Report (Internal)
Issue identified and documented. Users unable to log in since Azure AD config change. Critical priority. 

### [TO BE FILLED BY EXTERNAL PC]
Investigation and fix notes...

---

## Resolution Notes
(To be filled when resolved)

### Root Cause
[What actually caused the issue]

### Solution Implemented
[What code changes fixed it]

### Files Changed
- [ ] backend/app/...
- [ ] frontend/src/...

### Verification
- [ ] Tested on External PC (development)
- [ ] Tested on Internal Server (production)
- [ ] All test checklist items passed
- [ ] No regressions observed

### Lessons Learned
[What we learned and how to prevent similar issues]

---

**Status Updates**
- 2025-10-18 14:30: Issue created and documented (Internal)
- [Date/Time]: Status updated...
```

---

## 🔄 Production Workflow Steps

### **Phase 1: Issue Discovery (Internal Server)**

**When**: User reports bug or you discover issue during testing

**Steps**:

```bash
# 1. Navigate to issues folder
cd issues/open/

# 2. Determine priority and create folder if needed
mkdir P1-critical   # If critical issue
mkdir P2-high       # If high priority
mkdir P3-normal     # If normal priority

# 3. Create issue file from template
cp ../_templates/issue-template.md P1-critical/issue-001-login-azure-ad-fails.md

# 4. Fill in the template
notepad P1-critical/issue-001-login-azure-ad-fails.md

# Important: Be thorough!
# - Exact steps to reproduce
# - Complete error messages
# - All relevant logs
# - What you tried already
# - Sanitize sensitive data!

# 5. Review for sensitive data
# Check for:
# - Real credentials
# - Internal IPs/URLs
# - User personal data
# - Company secrets
# Replace with [REDACTED] or generic placeholders

# 6. Commit ONLY the issue file
git status  # Verify only the .md file is staged
git add issues/open/P1-critical/issue-001-login-azure-ad-fails.md
git commit -m "Issue #001 (P1): Login with Azure AD fails - audience mismatch"

# 7. Push to GitHub
git push origin main
```

---

### **Phase 2: Issue Processing (External PC)**

**When**: Daily check or notification of new issues

**Steps**:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Check for new issues
ls issues/open/P1-critical/
ls issues/open/P2-high/
ls issues/open/P3-normal/

# 3. Read the issue thoroughly
notepad issues/open/P1-critical/issue-001-login-azure-ad-fails.md

# Take notes:
# - What's the actual problem?
# - Can I reproduce locally?
# - What files need changes?
# - Do I need more information?

# 4. If you need more info, update the issue
# Add questions/requests to the issue file
git add issues/open/P1-critical/issue-001-login-azure-ad-fails.md
git commit -m "Issue #001: Request additional error details"
git push origin main
# Then wait for Internal to provide more info

# 5. If you have enough info, start fixing
# Move to in-progress
git mv issues/open/P1-critical/issue-001-login-azure-ad-fails.md issues/in-progress/

# 6. Update issue status
# Edit file, change status to "In Progress"
# Add investigation notes

# 7. Commit the move
git add issues/
git commit -m "Issue #001: Investigating Azure AD token validation"
git push origin main

# 8. Implement the fix
# ... edit code files ...
# ... test locally ...

# 9. Commit the fix
git add backend/app/core/security.py
git commit -m "Fix #001: Correct Azure AD audience validation

- Updated token validation to check correct audience claim
- Added logging for token validation failures
- Fixed audience mismatch error

Closes issue #001"

# 10. Update issue with fix details
# Edit issue file with:
# - What you changed
# - Why it should fix the problem
# - What to test

git add issues/in-progress/issue-001-login-azure-ad-fails.md
git commit -m "Issue #001: Fix implemented, ready for testing"

# 11. Push everything
git push origin main
```

---

### **Phase 3: Testing (Internal Server)**

**When**: Fix has been pushed from External PC

**Steps**:

```bash
# 1. Pull latest changes (code + issue updates)
git pull origin main

# 2. Review what changed
git log -5 --oneline
git show HEAD  # See the fix

# 3. Restart services
# ... restart backend/frontend ...

# 4. Test according to issue checklist
# Follow the "Testing Checklist" from the issue

# 5. Update issue with results

# If WORKS ✅:
# Move issue to resolved
git mv issues/in-progress/issue-001-login-azure-ad-fails.md issues/resolved/

# Update issue file:
# - Change status to "Resolved"
# - Fill in resolution notes
# - Add verification details

git add issues/resolved/issue-001-login-azure-ad-fails.md
git commit -m "Issue #001: Resolved - Login now works correctly

Tested with:
- 3 different user accounts
- Admin and regular user roles
- Multiple browsers
- Session persistence verified

All tests passed. Issue is resolved."

git push origin main

# If DOESN'T WORK ❌:
# Update issue with failure details

# Edit issue file:
# - Add new error messages
# - Add new logs
# - Clarify what still doesn't work
# - Suggest what else to check

git add issues/in-progress/issue-001-login-azure-ad-fails.md
git commit -m "Issue #001: Fix partially works but new error appeared

Original error fixed, but now getting:
[new error details]

Additional logs attached. Please investigate token expiration logic."

git push origin main

# Back to External PC for iteration
```

---

## 🔁 The Iteration Loop

### **Handling "Never-Ending Loop"**

If issue isn't fixed after 3 iterations:

**1. Schedule Synchronous Communication**

```markdown
# In issue file:

## Escalation Notes
After 3 fix attempts, issue still persists.

Proposed: Live debugging session
Options:
1. Screen share via Teams
2. Detailed video recording of issue
3. Enable remote debugging temporarily
4. Add extensive logging and capture full trace

Suggest option #2: I'll record a video showing exact behavior.
```

**2. Add Comprehensive Logging**

```python
# Add temporary detailed logging
import logging
logger = logging.getLogger(__name__)

def validate_token(token: str):
    logger.debug(f"Token validation started")
    logger.debug(f"Token length: {len(token)}")
    logger.debug(f"Token starts with: {token[:20]}...")
    
    # ... validation logic ...
    
    logger.debug(f"Validation result: {result}")
    return result
```

**3. Break Down Into Smaller Steps**

```markdown
# In issue file:

## Debugging Protocol

Step 1: Verify token is received
- [ ] Add log immediately when token arrives
- [ ] Push fix
- [ ] Test on internal
- [ ] Confirm token is received correctly

Step 2: Verify token format
- [ ] Add log showing token structure
- [ ] Push fix
- [ ] Test on internal
- [ ] Confirm token format matches expectations

(Continue breaking down...)
```

---

## 📊 Issue Tracking

### **Daily Issue Review (External PC)**

```bash
# Create a simple status script
# save-as: scripts/check-issues.sh

#!/bin/bash

echo "═══════════════════════════════════"
echo "   ISSUE STATUS DASHBOARD"
echo "═══════════════════════════════════"
echo ""

echo "🔥 CRITICAL (P1):"
ls -1 issues/open/P1-critical/ 2>/dev/null | wc -l
ls -1 issues/open/P1-critical/ 2>/dev/null | sed 's/^/  - /'

echo ""
echo "⚠️  HIGH (P2):"
ls -1 issues/open/P2-high/ 2>/dev/null | wc -l
ls -1 issues/open/P2-high/ 2>/dev/null | sed 's/^/  - /'

echo ""
echo "📋 NORMAL (P3):"
ls -1 issues/open/P3-normal/ 2>/dev/null | wc -l
ls -1 issues/open/P3-normal/ 2>/dev/null | sed 's/^/  - /'

echo ""
echo "🔧 IN PROGRESS:"
ls -1 issues/in-progress/ 2>/dev/null | wc -l
ls -1 issues/in-progress/ 2>/dev/null | sed 's/^/  - /'

echo ""
echo "✅ RECENTLY RESOLVED:"
ls -1t issues/resolved/ 2>/dev/null | head -5 | sed 's/^/  - /'

echo ""
echo "═══════════════════════════════════"
```

Run daily:
```bash
bash scripts/check-issues.sh
```

### **Weekly Issue Analysis**

Track metrics to improve:

```markdown
# Weekly review template

## Week of [Date]

### Issues Opened: X
- P1: X
- P2: X
- P3: X

### Issues Resolved: X
- Average resolution time: X days

### Issues Still Open: X
- Oldest: [issue-name] (X days old)

### Patterns Observed
- Common issue types: ...
- Root causes: ...

### Process Improvements
- What worked well: ...
- What needs improvement: ...
- Action items: ...
```

---

## 🔒 Security Considerations

### **What CAN Be in Issue Files**

✅ **Safe Information**:
- Error messages (generic patterns)
- Reproduction steps (anonymized)
- Expected vs actual behavior
- File names and line numbers
- Generic configuration needs
- Test procedures
- Technical analysis

✅ **Examples**:
```markdown
# SAFE
- Error: "Token validation failed - audience mismatch"
- Steps: "Login with test-user@company.com, then click X"
- Config needed: "Azure AD tenant ID must match..."
- Files affected: "backend/app/core/security.py line 45"
```

### **What CANNOT Be in Issue Files**

❌ **Sensitive Information**:
- Actual credentials or API keys
- Real user email addresses or data
- Internal IP addresses or URLs
- Company-specific business logic details
- Actual Azure AD tenant IDs
- Database passwords or connection strings

❌ **Examples to Avoid**:
```markdown
# UNSAFE - DON'T DO THIS!
- Azure Tenant ID: 12345678-abcd-efgh-ijkl-mnopqrstuvwx
- Database: postgresql://admin:Pass123@10.0.1.50:5432/prod
- User: john.doe@company.com reported issue
- Internal URL: http://company-internal-api.local/secret
```

### **Sanitization Checklist**

Before pushing any issue file:

- [ ] Replace real Azure AD IDs with [REDACTED] or "company-tenant-id"
- [ ] Replace real user emails with "test-user@company.com"
- [ ] Replace internal URLs with "internal-server.company.local"
- [ ] Replace internal IPs with "10.x.x.x" or "[internal-ip]"
- [ ] Remove any passwords or API keys
- [ ] Remove any user personal data
- [ ] Generalize company-specific business logic

---

## 🎯 Best Practices

### **Writing Good Issue Documentation**

**DO**:
- ✅ Be specific and detailed
- ✅ Include exact error messages
- ✅ Provide complete reproduction steps
- ✅ Add relevant logs (sanitized)
- ✅ List what you already tried
- ✅ Include testing checklist
- ✅ Update status regularly

**DON'T**:
- ❌ Be vague ("login doesn't work")
- ❌ Skip reproduction steps
- ❌ Assume context ("you know what I mean")
- ❌ Include sensitive data
- ❌ Leave status stale
- ❌ Create duplicate issues

### **Effective Communication**

**Good Example**:
```markdown
## Problem
After Azure AD authentication, user sees "Invalid token" error.

## Reproduction
1. Go to /login
2. Click "Azure AD"
3. Login with test-user@company.com
4. See error on redirect

## Error
Backend log shows: "Audience mismatch: expected api://[app-id], got api://[different-id]"

## Hypothesis
AZURE_AD_CLIENT_ID in .env might not match Azure Portal registration.

## Request
Please check security.py line 45, token validation logic.
```

**Bad Example**:
```markdown
## Problem
Login broken

## Info
Doesn't work

## Need
Fix it
```

---

## 📚 Templates & Examples

All templates are stored in `issues/_templates/`:

- `issue-template.md` - Full issue documentation template
- `issue-quick.md` - Quick issue template for simple bugs
- `issue-feature-request.md` - Template for feature requests
- `ISSUE_WORKFLOW.md` - Summary of this workflow

---

## ✅ Production Workflow Checklist

### **Setup (One-Time)**
- [ ] Create `issues/` folder structure
- [ ] Copy templates to `issues/_templates/`
- [ ] Create issue dashboard script
- [ ] Document workflow for team
- [ ] Test with sample issue

### **Issue Creation (Internal)**
- [ ] Copy template
- [ ] Fill all sections thoroughly
- [ ] Sanitize sensitive data
- [ ] Review with safety checklist
- [ ] Commit only .md file
- [ ] Push to GitHub

### **Issue Resolution (External)**
- [ ] Pull latest issues
- [ ] Read issue thoroughly
- [ ] Move to in-progress
- [ ] Implement fix
- [ ] Update issue with fix details
- [ ] Push code and issue updates

### **Issue Verification (Internal)**
- [ ] Pull latest changes
- [ ] Test according to checklist
- [ ] Update issue with results
- [ ] Move to resolved (if works)
- [ ] Or document remaining issues (if doesn't work)

---

## 🔄 Migration from Current Workflow

**When you're ready to activate this workflow:**

1. **Create folder structure**:
   ```bash
   mkdir -p issues/_templates
   mkdir -p issues/open/{P1-critical,P2-high,P3-normal}
   mkdir -p issues/in-progress
   mkdir -p issues/resolved
   ```

2. **Copy templates**:
   - Move template files from this document into `issues/_templates/`

3. **Test with example issue**:
   - Create `issues/resolved/issue-000-example.md`
   - Fill with example data
   - Practice the workflow

4. **Update team documentation**:
   - Add section to main README
   - Update WORKFLOW_GUIDE.md with link to this document

5. **Start using for real issues**:
   - First real issue is #001
   - Follow workflow strictly
   - Iterate and improve

---

**Remember**: This workflow is for production phase. During development, use the simpler workflow in [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)!

