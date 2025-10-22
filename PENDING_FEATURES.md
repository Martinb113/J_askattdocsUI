# 🔮 PENDING FEATURES & FUTURE DEVELOPMENT

> **Last Updated**: 2025-10-22
> **Project Status**: ~90% complete for MVP
> **Branching Strategy**: Create feature branch from `development` for each feature

---

## 🚨 HIGH PRIORITY

### ✅ Feature 0: Admin Role Display Fix
**Status**: ✅ COMPLETED (2025-10-22)
**Branch**: `fix/admin-role-display`
**Description**: Fixed admin panel showing dashes instead of role names
**Files Modified**:
- `backend/app/schemas/admin.py` - Added `AdminUserResponse` with full `RoleResponse` objects
- `backend/app/api/v1/admin.py` - Updated endpoints to return full role objects
- Frontend already compatible with role objects

---

### 1. 🔧 Message Feedback Fix
**Status**: ⏳ IN PROGRESS
**Priority**: 🚨 HIGH
**Branch**: `feature/feedback-fix` (to be created from `development`)
**Estimated Time**: 3-4 hours

**Issue**: Feedback functionality only works for messages loaded from database, not for newly created streaming messages

**Root Cause**:
- Messages created during streaming have temporary IDs (`Date.now().toString()`)
- Backend saves message with real UUID but doesn't return it in SSE stream
- Frontend keeps using temporary ID

**Solution**:
1. Backend: Add new SSE event type `message_id` that returns the real database ID
2. Backend: Emit `message_id` event after saving message to database
3. Frontend: Update message ID when receiving `message_id` event
4. Frontend: Enable feedback button only after receiving real message ID

**Files to Modify**:
- `backend/app/api/v1/chat.py` - Add `message_id` SSE event
- `backend/app/schemas/chat.py` - Add `SSEMessageIdEvent` type
- `frontend/src/types/index.ts` - Add `SSEMessageIdEvent` interface
- `frontend/src/pages/Chat.tsx` - Handle `message_id` event and update state

**Implementation Steps**:
1. ✅ Create branch `feature/feedback-fix` from `development`
2. ⏳ Backend: Add `SSEMessageIdEvent` schema
3. ⏳ Backend: Emit message ID after saving to database
4. ⏳ Frontend: Add message ID event handler
5. ⏳ Frontend: Update assistant message ID when received
6. ⏳ Test feedback on newly created messages
7. ⏳ Merge to `development` after testing

---

### 2. 🔄 Configuration Auto-Population API
**Status**: ⏳ PENDING
**Priority**: 🚨 HIGH
**Branch**: `feature/config-auto-fetch` (to be created)
**Estimated Time**: 4-6 hours
**Issue**: #4 in `zzz_issues.md`

**Description**: Implement API to automatically fetch and populate configurations from domain-services

**API Details**:
- **Stage**: `https://cast-southcentral-nprd-apim-02.azure-api.net/stage/domain-services/admin/list-config-by-domain`
- **Prod**: `https://askatt-clientservices.web.att.com/domain-services/admin/list-config-by-domain`

**Request**:
```json
{
  "domain": "8970wikik",
  "log_as_userid": "attid"
}
```

**Response**:
```json
[
  {
    "_id": "8970wikik-sd_config_v3",
    "domain": "8970wikik",
    "version": "sd_config_v3",
    "domainName": "SD_International",
    "created_on": "2024-11-28T09:09:25.479Z"
  }
]
```

**Implementation Tasks**:
- Backend: Create `/api/v1/admin/configurations/fetch-by-domain` endpoint
- Backend: Add service function to call external API
- Backend: Parse response and create/update Configuration records
- Backend: Link configurations to appropriate roles
- Frontend: Add "Fetch Configurations" button in Admin panel
- Frontend: Show loading state and success/error messages
- Frontend: Refresh configuration list after successful fetch

**Files to Create/Modify**:
- `backend/app/schemas/admin.py` - Add request/response schemas
- `backend/app/services/askdocs_config.py` - Add fetch function
- `backend/app/api/v1/admin.py` - Add new endpoint
- `frontend/src/pages/Admin.tsx` - Add fetch UI

---

## 📋 MEDIUM PRIORITY

### 3. 🎨 Enhanced Configuration Management UI
**Status**: ⏳ PENDING
**Priority**: 📋 MEDIUM
**Branch**: `feature/config-management` (to be created)
**Estimated Time**: 6-8 hours

**Current**: Admin can view all configurations
**Needed**:
- ✅ View configurations (DONE)
- ⏳ Create new configurations manually
- ⏳ Edit existing configurations
- ⏳ Delete configurations
- ⏳ Toggle active/inactive status
- ⏳ Assign roles to configurations
- ⏳ Bulk import from API (see #2 above)
- ⏳ Filter by domain/environment
- ⏳ Search configurations

**Files**: `frontend/src/pages/Admin.tsx`, `backend/app/api/v1/admin.py`

---

### 4. 👥 Role Management Enhancements
**Status**: ⏳ PENDING
**Priority**: 📋 MEDIUM
**Branch**: `feature/role-management` (to be created)
**Estimated Time**: 4-6 hours

**Current**: Admin can view roles and assign to users
**Needed**:
- ✅ View all roles (DONE)
- ✅ Assign roles to users (DONE)
- ⏳ Create new roles with display_name
- ⏳ Edit role display names and descriptions
- ⏳ Delete unused roles
- ⏳ View which users have each role
- ⏳ Bulk role assignment
- ⏳ Role permissions matrix view

**Files**: `frontend/src/pages/Admin.tsx`, `backend/app/api/v1/admin.py`

---

### 5. 👤 User Management Enhancements
**Status**: ⏳ PENDING
**Priority**: 📋 MEDIUM
**Branch**: `feature/user-management` (to be created)
**Estimated Time**: 4-6 hours

**Current**: Admin can view users and assign roles
**Needed**:
- ✅ View all users (DONE)
- ✅ Assign roles to users (DONE)
- ⏳ Deactivate/reactivate users
- ⏳ Reset user passwords (admin function)
- ⏳ View user activity logs
- ⏳ Search and filter users
- ⏳ Export user list
- ⏳ User statistics (message count, token usage, etc.)

**Files**: `frontend/src/pages/Admin.tsx`, `backend/app/api/v1/admin.py`

---

### 6. 🔍 Conversation Search & Filters
**Status**: ⏳ PENDING
**Priority**: 📋 MEDIUM
**Branch**: `feature/conversation-search` (to be created)
**Estimated Time**: 4-6 hours

**Current**: Search input displayed but not functional
**Needed**:
- ⏳ Search conversations by title
- ⏳ Search conversations by message content
- ⏳ Filter by service type (AskAT&T vs AskDocs)
- ⏳ Filter by date range
- ⏳ Filter by configuration
- ⏳ Sort options (date, title, message count)
- ⏳ Pagination for large conversation lists

**Files**: `frontend/src/components/ConversationList.tsx`, `backend/app/api/v1/chat.py`

---

### 7. 📊 Token Usage Analytics & Reporting
**Status**: ⏳ PENDING
**Priority**: 📋 MEDIUM
**Branch**: `feature/usage-analytics` (to be created)
**Estimated Time**: 6-8 hours

**Current**: `/api/v1/admin/stats/usage` returns placeholder data
**Needed**:
- ⏳ Fix token aggregation from messages
- ⏳ Parse JSONB token_usage field properly
- ⏳ Daily/weekly/monthly usage reports
- ⏳ Per-user usage statistics
- ⏳ Per-configuration usage statistics
- ⏳ Cost estimation based on token usage
- ⏳ Visual charts and graphs
- ⏳ Export reports to CSV/Excel

**Files**:
- `backend/app/api/v1/admin.py` (lines 398-451)
- New frontend component needed

---

## 🎨 LOW PRIORITY / NICE-TO-HAVE

### 8. 💬 Conversation Management Features
**Status**: ⏳ PENDING
**Priority**: 🎨 LOW
**Branch**: `feature/conversation-management` (to be created)
**Estimated Time**: 8-10 hours

**Features**:
- ⏳ Edit conversation titles
- ⏳ Add tags/labels to conversations
- ⏳ Star/favorite important conversations
- ⏳ Archive old conversations
- ⏳ Export conversation to PDF/text
- ⏳ Share conversation (generate shareable link)
- ⏳ Conversation folders/organization

---

### 9. ✏️ Message Enhancements
**Status**: ⏳ IN PROGRESS
**Priority**: 🎨 LOW (High for user experience)
**Branch**: `feature/message-enhancements` (to be created from `development`)
**Estimated Time**: 3-4 hours

**Features**:
- ⏳ Copy message to clipboard (with button)
- ⏳ Regenerate AI responses
- ⏳ Edit sent messages (future)
- ⏳ Message reactions/likes (future)
- ⏳ Message bookmarking (future)
- ⏳ Message search within conversation (future)

**Implementation Priority**:
1. **Phase 1** (Immediate): Copy to clipboard
2. **Phase 2** (Next): Regenerate responses
3. **Phase 3** (Future): Edit, reactions, bookmarking

**Files to Modify**:
- `frontend/src/pages/Chat.tsx` - Add copy and regenerate buttons
- `frontend/src/components/ui/Button.tsx` - May need icon button variant
- `backend/app/api/v1/chat.py` - Support regenerate with same prompt

---

### 10. 📚 Source Citation Improvements (AskDocs)
**Status**: ⏳ IN PROGRESS
**Priority**: 🎨 LOW (High for AskDocs users)
**Branch**: `feature/citation-improvements` (to be created from `development`)
**Estimated Time**: 4-6 hours

**Current**: Sources displayed as simple list
**Needed**:
- ✅ Display sources with titles and URLs (DONE)
- ⏳ Click to expand source details (modal or expandable)
- ⏳ Show source metadata (chunk_id, scores)
- ⏳ Highlight relevant passages from `captions.highlights`
- ⏳ Show confidence/relevance scores (aisearch_score, reranker_score)
- ⏳ Filter/sort sources by relevance
- ⏳ Preview source content in modal
- ⏳ Copy source citation

**Implementation Priority**:
1. **Phase 1** (Immediate): Expandable source details
2. **Phase 2** (Next): Show highlights and scores
3. **Phase 3** (Future): Preview modal, filtering

**Files to Modify**:
- `frontend/src/pages/Chat.tsx` - Enhanced source rendering
- `frontend/src/types/index.ts` - May need extended Source interface
- New component: `frontend/src/components/SourceCard.tsx` (optional)

---

### 11. ⚙️ User Preferences & Settings
**Status**: ⏳ PENDING
**Priority**: 🎨 LOW
**Branch**: `feature/user-preferences` (to be created)
**Estimated Time**: 6-8 hours

**Features**:
- ⏳ Theme selection (light/dark mode)
- ⏳ Font size preferences
- ⏳ Notification preferences
- ⏳ Default service selection
- ⏳ Keyboard shortcuts
- ⏳ Language preferences
- ⏳ Email notifications for feedback

---

### 12. 📝 Audit Logging
**Status**: ⏳ PENDING
**Priority**: 🎨 LOW
**Branch**: `feature/audit-logging` (to be created)
**Estimated Time**: 8-10 hours

**Features**:
- ⏳ Log all admin actions (user created, role assigned, config changed)
- ⏳ Log authentication events
- ⏳ Log API calls and errors
- ⏳ Audit trail viewer for admins
- ⏳ Export audit logs

---

### 13. 📈 Performance Monitoring
**Status**: ⏳ PENDING
**Priority**: 🎨 LOW
**Branch**: `feature/performance-monitoring` (to be created)
**Estimated Time**: 10-12 hours

**Features**:
- ⏳ Response time tracking
- ⏳ Error rate monitoring
- ⏳ API health dashboard
- ⏳ Alert system for failures
- ⏳ Performance metrics per configuration

---

### 14. 📖 Documentation & Help
**Status**: ⏳ PENDING
**Priority**: 🎨 LOW
**Branch**: `feature/in-app-help` (to be created)
**Estimated Time**: 8-10 hours

**Features**:
- ⏳ In-app help/tutorials
- ⏳ FAQ section
- ⏳ Video tutorials
- ⏳ Interactive onboarding for new users
- ⏳ Changelog visible in app
- ⏳ API documentation generator

---

### 15. 🔎 Advanced Search
**Status**: ⏳ PENDING
**Priority**: 🎨 LOW
**Branch**: `feature/advanced-search` (to be created)
**Estimated Time**: 6-8 hours

**Features**:
- ⏳ Full-text search across all conversations
- ⏳ Advanced query builder
- ⏳ Saved search queries
- ⏳ Search history

---

## 🔐 PRODUCTION READINESS

### 16. 🔌 Replace MOCK Services
**Status**: ⏳ PENDING
**Priority**: 🔐 PRODUCTION
**Branch**: `feature/production-apis` (to be created)
**Estimated Time**: 4-6 hours

**Current**: Running in MOCK mode for development
**Tasks**:
- ⏳ Switch `USE_MOCK_AZURE_AD=false`
- ⏳ Add real Azure AD credentials
- ⏳ Switch `USE_MOCK_ASKATT=false`
- ⏳ Add real AskAT&T API credentials
- ⏳ Switch `USE_MOCK_ASKDOCS=false`
- ⏳ Add real AskDocs API credentials
- ⏳ Test real API integrations
- ⏳ Handle API errors gracefully
- ⏳ Add retry logic for failed requests

**Files**: `backend/.env`, `backend/app/main.py`

---

### 17. 🔒 Security Enhancements
**Status**: ⏳ PENDING
**Priority**: 🔐 PRODUCTION
**Branch**: `feature/security-enhancements` (to be created)
**Estimated Time**: 8-10 hours

**Features**:
- ⏳ Rate limiting per user
- ⏳ IP-based rate limiting
- ⏳ Session management improvements
- ⏳ Two-factor authentication (2FA)
- ⏳ Password complexity requirements enforcement
- ⏳ Account lockout after failed attempts
- ⏳ Security headers (CSP, HSTS, etc.)
- ⏳ Regular security audits

---

### 18. 🧪 Testing
**Status**: ⏳ PENDING
**Priority**: 🔐 PRODUCTION
**Branch**: `feature/comprehensive-testing` (to be created)
**Estimated Time**: 20-30 hours

**Coverage**:
- ⏳ Unit tests for backend services
- ⏳ Integration tests for API endpoints
- ⏳ E2E tests for critical user flows
- ⏳ Load testing for performance
- ⏳ Frontend component tests
- ⏳ API contract tests

---

### 19. 🚀 Deployment & DevOps
**Status**: ⏳ PENDING
**Priority**: 🔐 PRODUCTION
**Branch**: `feature/cicd-pipeline` (to be created)
**Estimated Time**: 15-20 hours

**Tasks**:
- ⏳ CI/CD pipeline setup
- ⏳ Automated testing in pipeline
- ⏳ Docker containerization
- ⏳ Kubernetes deployment configs
- ⏳ Environment-specific configs
- ⏳ Database migration strategy
- ⏳ Backup and disaster recovery
- ⏳ Monitoring and alerting setup

---

## 📊 SUMMARY

**Total Features**: 20 (including completed role display fix)

**Status Breakdown**:
- ✅ **Completed**: 1 feature
- 🔧 **In Progress**: 3 features (#1, #9, #10)
- ⏳ **Pending**: 16 features

**Priority Breakdown**:
- 🚨 **High Priority**: 2 features
- 📋 **Medium Priority**: 5 features
- 🎨 **Low Priority**: 8 features
- 🔐 **Production**: 4 features

**Time Estimates**:
- High Priority Features: 7-10 hours
- Medium Priority Features: 24-34 hours
- Low Priority Features: 55-72 hours
- Production Features: 47-66 hours
- **Total**: 133-182 hours

**Current Project Status**: ~90% complete for MVP
**Next Focus**: Features #1, #9, #10

---

## 🔄 BRANCHING STRATEGY

```
main (production)
  └── development (integration)
      ├── feature/feedback-fix (#1) ⏳ IN PROGRESS
      ├── feature/message-enhancements (#9) ⏳ IN PROGRESS
      ├── feature/citation-improvements (#10) ⏳ IN PROGRESS
      ├── feature/config-auto-fetch (#2) - NEXT
      ├── feature/config-management (#3)
      ├── feature/role-management (#4)
      └── ... (other features)
```

**Workflow**:
1. Create feature branch from `development`
2. Implement and test feature
3. Create PR to merge into `development`
4. After testing in `development`, merge to `main`

---

## 📝 NOTES

- This file should be updated as features are completed or priorities change
- Branch names follow convention: `feature/descriptive-name` or `fix/descriptive-name`
- Each feature should have its own PR for better tracking and review
- High priority features should be completed before medium/low priority
- Production features should be tackled together as a cohesive release

**Last Updated By**: Claude Code
**Next Review Date**: After completion of features #1, #9, #10
