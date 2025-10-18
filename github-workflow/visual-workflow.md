# Visual Workflow Diagram

## 🎨 Complete Workflow Visualization

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    EXTERNAL PC (Development)                  ┃
┃                                                                ┃
┃  Day 1: Start Feature                                         ┃
┃  ┌──────────┐                                                 ┃
┃  │ develop  │                                                 ┃
┃  └────┬─────┘                                                 ┃
┃       │ git checkout -b feature/login-fix                     ┃
┃       ↓                                                        ┃
┃  ┌─────────────────────┐                                      ┃
┃  │ feature/login-fix   │  ← Work here                         ┃
┃  │  (commits...)       │                                      ┃
┃  └─────────┬───────────┘                                      ┃
┃            │ git push origin feature/login-fix                ┃
┃            ↓                                                   ┃
┗━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
             │
             ↓
    ┌────────────────┐
    │    GITHUB      │
    │  (Repository)  │
    └────────────────┘
             │
             ↓
┏━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            │               EXTERNAL PC                         ┃
┃  Day 2: Merge Feature                                         ┃
┃            │                                                   ┃
┃            ↓ git checkout develop                             ┃
┃       ┌──────────┐                                            ┃
┃       │ develop  │ ← git merge feature/login-fix              ┃
┃       └────┬─────┘                                            ┃
┃            │ git push origin develop                          ┃
┃            ↓                                                   ┃
┗━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
             │
             ↓
    ┌────────────────┐
    │    GITHUB      │
    │  develop ✓     │
    └────────────────┘
             │
             ↓
┏━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            │         INTERNAL SERVER (Testing)                ┃
┃  Day 2: Test New Feature                                      ┃
┃            ↓ git pull origin develop                          ┃
┃       ┌──────────┐                                            ┃
┃       │ develop  │  ← Test with real environment              ┃
┃       └────┬─────┘                                            ┃
┃            │ Tests pass ✓                                     ┃
┃            │                                                   ┃
┗━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
             │
             │ Report: "Works great!"
             ↓
┏━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            │         EXTERNAL PC (Release)                    ┃
┃  Day 3: Promote to Production                                 ┃
┃            │                                                   ┃
┃       ┌──────────┐   git merge develop                        ┃
┃       │   main   │ ← ─────────┐                               ┃
┃       └────┬─────┘            │                               ┃
┃            │             ┌──────────┐                          ┃
┃            │             │ develop  │                          ┃
┃            │             └──────────┘                          ┃
┃            │ git push origin main                             ┃
┃            ↓                                                   ┃
┗━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
             │
             ↓
    ┌────────────────┐
    │    GITHUB      │
    │  main ✓        │
    └────────────────┘
             │
             ↓
┏━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            │         INTERNAL SERVER (Production)             ┃
┃  Day 3: Deploy Stable Version                                 ┃
┃            ↓ git pull origin main                             ┃
┃       ┌────────┐                                              ┃
┃       │  main  │  ← Running in production                     ┃
┃       └────────┘                                              ┃
┃                                                                ┃
┃       🎉 Feature deployed to production!                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🔄 Multiple Features in Parallel

```
develop
  ├── feature/auth-fix      (Developer working here)
  ├── feature/chat-export   (Developer working here)
  └── feature/ui-redesign   (Developer working here)

Each feature:
  1. Created from develop
  2. Worked on independently
  3. Merged back to develop when ready
  4. Tested in develop
  5. Eventually promoted to main together
```

---

## 🚨 Bug Found in Production

```
┌────────────────────────────────────────────────────────┐
│ INTERNAL SERVER (Production)                           │
│                                                         │
│ 🐛 Bug discovered in main branch                       │
│                                                         │
│ Option 1: Document issue                               │
│ - Create issue-XXX.md                                  │
│ - Push ONLY the issue file                             │
│ - External PC fixes it                                 │
└────────────────┬───────────────────────────────────────┘
                 │
                 ↓
        ┌────────────────┐
        │    GITHUB      │
        │  issue-XXX.md  │
        └────────────────┘
                 │
                 ↓
┌────────────────┴───────────────────────────────────────┐
│ EXTERNAL PC (Development)                              │
│                                                         │
│ 1. Pull issue file                                     │
│ 2. Create feature/fix-issue-XXX                        │
│ 3. Fix the bug                                         │
│ 4. Push to develop                                     │
└────────────────┬───────────────────────────────────────┘
                 │
                 ↓
        ┌────────────────┐
        │    GITHUB      │
        │  develop ✓     │
        └────────────────┘
                 │
                 ↓
┌────────────────┴───────────────────────────────────────┐
│ INTERNAL SERVER (Testing)                              │
│                                                         │
│ 1. Pull develop                                        │
│ 2. Test fix                                            │
│ 3. If works: External PC merges to main                │
│ 4. Pull main                                           │
│ 5. 🎉 Bug fixed!                                       │
└────────────────────────────────────────────────────────┘
```

---

## 🔐 Configuration vs Code Flow

```
┌─────────────────────┐         ┌─────────────────────┐
│   EXTERNAL PC       │         │  INTERNAL SERVER    │
├─────────────────────┤         ├─────────────────────┤
│                     │         │                     │
│  CODE:              │  sync   │  CODE:              │
│  ✓ Same Python      │◄───────►│  ✓ Same Python      │
│  ✓ Same React       │  via    │  ✓ Same React       │
│  ✓ Same logic       │  GitHub │  ✓ Same logic       │
│                     │         │                     │
├─────────────────────┤         ├─────────────────────┤
│                     │         │                     │
│  CONFIG:            │ ✗ never │  CONFIG:            │
│  .env (dev)         │  sync   │  .env (production)  │
│  - Mock auth        │         │  - Real Azure AD    │
│  - SQLite           │         │  - PostgreSQL       │
│  - Debug logging    │         │  - Production keys  │
│  - localhost        │         │  - Company URLs     │
│                     │         │                     │
└─────────────────────┘         └─────────────────────┘
```

---

## 🎯 Decision Flow: Which Branch?

```
                    START
                      │
                      ↓
         Are you on External PC or Internal Server?
                      │
        ┌─────────────┴─────────────┐
        │                           │
    External PC              Internal Server
        │                           │
        ↓                           ↓
  Are you developing        Are you deploying
  a new feature?            to production?
        │                           │
    ┌───┴───┐                   ┌───┴───┐
    │       │                   │       │
   Yes     No                  Yes     No
    │       │                   │       │
    ↓       ↓                   ↓       ↓
  Create   Work on            Use    Use
  feature/  develop           main   develop
  branch    branch            
    │       │                   │       │
    └───┬───┘                   └───┬───┘
        │                           │
        ↓                           ↓
    Push to                     Pull only
    GitHub                      (never push)
```

---

## 📊 Branch Protection Visualization

```
┌──────────────────────────────────────────────────────┐
│                     main (protected)                  │
│  ┌────────────────────────────────────────────────┐  │
│  │  ✓ Always stable                               │  │
│  │  ✓ Production ready                            │  │
│  │  ✓ Thoroughly tested                           │  │
│  │  ❌ Cannot push directly                        │  │
│  │  ✅ Only merge from develop                     │  │
│  └────────────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────────────┘
                     ↑ (merge only)
┌────────────────────┴─────────────────────────────────┐
│                  develop (integration)                │
│  ┌────────────────────────────────────────────────┐  │
│  │  ✓ Integration testing                         │  │
│  │  ✓ Should be stable                            │  │
│  │  ✓ Can have minor issues                       │  │
│  │  ✅ Receive feature merges                      │  │
│  │  ✅ Push allowed                                 │  │
│  └────────────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────────────┘
                     ↑ (merge features)
     ┌───────────────┼───────────────┐
     │               │               │
┌────┴────┐    ┌────┴────┐    ┌────┴────┐
│feature/ │    │feature/ │    │feature/ │
│auth-fix │    │chat-exp │    │ui-fix   │
└─────────┘    └─────────┘    └─────────┘
  (work)         (work)         (work)
```

---

**This visual guide complements the text documentation. Print it for quick reference!**

