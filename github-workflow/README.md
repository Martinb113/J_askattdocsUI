# GitHub Workflow Documentation

**Version**: 1.0  
**Last Updated**: October 18, 2025  
**Author**: Martin

---

## 📚 Documentation Index

This folder contains all documentation for managing the j_askdocs application across multiple environments (Internal Company Server and External Development PC).

### **Start Here** 👈

0. **[GETTING_STARTED.md](GETTING_STARTED.md)** - **READ THIS FIRST!** ⭐
   - 5-minute quick setup
   - Daily task examples
   - Troubleshooting guide
   - Perfect entry point for new users

### **Current Development Phase**

1. **[WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)** - Main workflow for daily development
   - Configuration-first approach
   - How to sync between environments
   - Daily commands and best practices

2. **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Setting up .env files
   - External PC configuration
   - Internal server configuration
   - Environment variables reference

3. **[SAFETY_CHECKLIST.md](SAFETY_CHECKLIST.md)** - Security checklist before pushing
   - What to check before git push
   - Common mistakes to avoid
   - Quick safety verification

4. **[PRE_COMMIT_HOOKS.md](PRE_COMMIT_HOOKS.md)** - Automated safety checks
   - How to set up pre-commit hooks
   - Preventing sensitive data leaks
   - Testing your hooks

### **Future Production Phase**

5. **[PRODUCTION_WORKFLOW.md](PRODUCTION_WORKFLOW.md)** - Issue-driven workflow for production
   - Issue documentation system
   - Testing loops with real users
   - Advanced synchronization strategies

---

## 🎯 Quick Start

👉 **START HERE**: [GETTING_STARTED.md](GETTING_STARTED.md) - Complete quick start guide

### **For External PC (Development)** - 2 Minutes

```powershell
# Navigate to project
cd C:\Users\admin\Documents\AI_projects\j_askdocs

# Setup environment
cd backend
copy env.development.template .env

# Start developing!
# (See GETTING_STARTED.md for detailed steps)
```

### **For Internal Server (Testing/Production)** - 5 Minutes

```bash
# Clone repository
git clone https://github.com/Martinb113/J_askattdocsUI.git
cd J_askattdocsUI

# Setup environment with REAL company credentials
cd backend
cp env.production.template .env
nano .env  # Edit with real credentials

# Pull latest updates daily
git pull origin main

# NEVER push code from internal server
# (See GETTING_STARTED.md for detailed setup)
```

---

## 🔒 Security First

**Golden Rules:**
1. ✅ `.env` files are NEVER committed to Git
2. ✅ Always review `git status` and `git diff` before pushing
3. ✅ Work primarily on External PC (safer)
4. ✅ Internal server pulls only, doesn't push code
5. ✅ Use pre-commit hooks for automated safety

---

## 📞 Need Help?

- **Workflow questions**: See [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)
- **Configuration issues**: See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- **Security concerns**: See [SAFETY_CHECKLIST.md](SAFETY_CHECKLIST.md)
- **Production planning**: See [PRODUCTION_WORKFLOW.md](PRODUCTION_WORKFLOW.md)

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-18 | Initial workflow documentation created |

