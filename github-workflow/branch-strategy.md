# Branch Strategy

## 🌳 Branch Structure (Dual-Track)

### `main` Branch
- **Purpose:** Production-ready code
- **Protection:** Cannot push directly
- **Updates:** Receives merges from BOTH `develop` AND `internal` after review
- **Deployed to:** Internal production server
- **Stability:** Always stable and tested

### `develop` Branch
- **Purpose:** External PC development
- **Updates:** Receives merges from feature branches
- **Testing:** Test on External PC
- **Owner:** External PC
- **Push:** External PC only

### `internal` Branch
- **Purpose:** Internal Server adjustments and fixes
- **Updates:** Created when Internal Server needs to make changes
- **Testing:** Test with production environment
- **Owner:** Internal Server
- **Push:** Internal Server only

### `feature/*` Branches
- **Purpose:** Individual features or fixes
- **Naming:** `feature/short-description`
- **Lifespan:** Temporary (deleted after merge)
- **Created from:** `develop`
- **Merged to:** `develop`

---

## 📋 Branch Rules

### Main Branch Rules
- ❌ No direct pushes
- ✅ Only merge from `develop` after testing
- ✅ Every merge creates a stable release
- ✅ Internal server runs this branch in production

### Develop Branch Rules
- ✅ Merge feature branches here
- ✅ Test thoroughly before promoting to `main`
- ❌ Don't merge broken features
- ✅ Can be deployed to internal server for testing

### Feature Branch Rules
- ✅ One feature/fix per branch
- ✅ Keep branches short-lived (hours/days, not weeks)
- ✅ Name clearly: `feature/auth-fix`, `feature/chat-streaming`
- ✅ Delete after merging

---

## 🔄 Branch Flow (Dual-Track)

```
External PC:
  1. feature/* → develop → push to GitHub

Internal Server:
  2. Pull develop → test → if changes needed → internal → push to GitHub

External PC (Review):
  3. Pull both develop + internal
  4. Review and align (resolve conflicts)
  5. Merge both to main
  6. Push main to GitHub

Internal Server (Deploy):
  7. Pull main → production deployment
```

**Key Point:** Both `develop` and `internal` work independently, then merge together into `main`.

---

## 🎯 Branch Selection Guide

### When to use each branch:

**Working on External PC:**
- Create `feature/` branches for new work
- Merge to `develop` when done
- Review and merge BOTH `develop` + `internal` to `main` when stable

**Working on Internal Server:**
- Pull `develop` for testing new features
- If changes needed → switch to `internal` branch
- Make fixes on `internal` and push back
- Pull `main` for production deployment

---

## 🛡️ Conflict Prevention

**Problem:** `develop` and `internal` diverge, conflicts when merging to `main`

**Solution:**
1. External PC: Regularly merge `develop` to `main`
2. Internal Server: Keep `internal` changes focused (production-specific fixes)
3. Before promoting to `main`: Review both branches together
4. Resolve conflicts in staging/review step, not in `main`

---

## 🔀 Merge Strategy

**When both branches have changes:**

```bash
# External PC:
git checkout develop
git pull origin develop
git pull origin internal   # Get internal changes
git merge internal         # Resolve conflicts here
# Test merged result
git checkout main
git merge develop          # Now safe to merge
git push origin main
```

**Result:** Both development tracks aligned before production release.

