# 🧪 Complete Testing Guide

**Quick Start**: Follow these steps to test all implemented features.

---

## 🚀 Step 1: Start Both Servers

### Terminal 1: Backend
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Expected**: Backend running at `http://localhost:8000`
**Verify**: Open `http://localhost:8000/docs` (Swagger UI should load)

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

**Expected**: Frontend running at `http://localhost:5173`
**Verify**: Browser should auto-open to login page

---

## 🧪 Step 2: Test Authentication & Phase 8a (UI/UX)

### Test 1: Signup
1. Go to `http://localhost:5173/signup`
2. Fill in form:
   - Full name: "Test User"
   - ATTID: "testuser"
   - Email: "test@example.com"
   - Password: "Test123!" (must have uppercase, lowercase, digit)
3. Click "Sign Up"
4. ✅ **Expected**: Auto-login + redirect to `/chat`
5. ✅ **Expected**: See "Started new conversation" toast (Phase 8a!)

### Test 2: Empty State
1. You should see a friendly empty state with:
   - Icon (MessageSquare)
   - "No messages yet" title
   - 3 example suggestions
2. ✅ **Expected**: No blank screen (Phase 8a!)

### Test 3: Send Message & Typing Indicator
1. Type "Hello, how are you?"
2. Press Enter
3. ✅ **Expected**: See 3 bouncing dots (typing indicator - Phase 8a!)
4. ✅ **Expected**: Dots disappear when streaming starts
5. ✅ **Expected**: Response streams token-by-token

### Test 4: Copy Button
1. Hover over the AI's response
2. ✅ **Expected**: Copy button appears in top-right (Phase 8a!)
3. Click the copy button
4. ✅ **Expected**: Icon changes to checkmark
5. ✅ **Expected**: Toast: "Copied to clipboard" (Phase 8a!)
6. Paste somewhere (Ctrl+V)
7. ✅ **Expected**: Message text pasted correctly

### Test 5: Feedback Toast
1. Click thumbs up on the message
2. ✅ **Expected**: Toast: "Thanks for the positive feedback!" (Phase 8a!)
3. Click thumbs down on another message
4. ✅ **Expected**: Toast: "Thank you for your feedback" (Phase 8a!)

### Test 6: Error Toast
1. Switch to "AskDocs" tab
2. Don't select a configuration
3. Try to send a message
4. ✅ **Expected**: Error toast: "Please select a configuration for AskDocs" (Phase 8a!)

---

## 📋 Step 3: Test Phase 6 (Conversation History)

### Test 1: Create Multiple Conversations
1. Click "New Chat" button
2. ✅ **Expected**: Toast: "Started new conversation" (Phase 8a!)
3. Send message to AskAT&T: "What is AI?"
4. Wait for response
5. Click "New Chat" again
6. Switch to AskDocs, select first configuration
7. Send message: "Explain machine learning"
8. Wait for response

### Test 2: Sidebar Verification
1. Look at left sidebar
2. ✅ **Expected**: See 2 conversations listed
3. ✅ **Expected**: Grouped under "Today"
4. ✅ **Expected**: Each has service badge (blue for AskAT&T, purple for AskDocs)
5. ✅ **Expected**: Titles generated from first messages:
   - "What is AI?"
   - "Explain machine learning"

### Test 3: Load Conversation
1. Click on first conversation in sidebar
2. ✅ **Expected**: Toast: "Conversation loaded" (Phase 8a!)
3. ✅ **Expected**: All messages from that conversation appear
4. ✅ **Expected**: Service type switches automatically
5. ✅ **Expected**: Conversation highlighted with blue left border

### Test 4: Search Conversations
1. Type "AI" in search box at top of sidebar
2. ✅ **Expected**: Only "What is AI?" conversation shown
3. Clear search
4. ✅ **Expected**: Both conversations show again

### Test 5: Delete Conversation
1. Hover over a conversation
2. Click trash icon
3. ✅ **Expected**: Confirmation dialog appears
4. Click OK
5. ✅ **Expected**: Toast: "Conversation deleted" (Phase 8a!)
6. ✅ **Expected**: Conversation removed from sidebar
7. ✅ **Expected**: If it was active, chat area shows empty state

### Test 6: Toggle Sidebar
1. Click hamburger menu (☰) in chat header
2. ✅ **Expected**: Sidebar smoothly slides out
3. Click hamburger again
4. ✅ **Expected**: Sidebar slides back in
5. ✅ **Expected**: Smooth 300ms animation

---

## 👨‍💼 Step 4: Test Phase 7 (Admin Panel)

### Test 1: Admin Login
1. Logout (click Logout button in header)
2. Login with admin credentials:
   - ATTID: `admin`
   - Password: `Admin123!`
3. ✅ **Expected**: Login successful + redirect to `/chat`

### Test 2: Admin Link Visibility
1. Look at header navigation
2. ✅ **Expected**: See "Admin" link next to "Chat" (only for admins!)
3. Click "Admin" link
4. ✅ **Expected**: Navigate to `/admin`

### Test 3: Admin Dashboard
1. ✅ **Expected**: Page title: "Admin Dashboard"
2. ✅ **Expected**: 3 tabs: Users, Roles, Configurations
3. ✅ **Expected**: Users tab active by default
4. ✅ **Expected**: Table with all users displayed

### Test 4: View Users
1. In Users table, you should see:
   - Admin user (you)
   - Test user (created earlier)
2. ✅ **Expected**: Each user shows:
   - Full name + ATTID
   - Email
   - Roles (badges)
   - "Assign Role" button

### Test 5: Assign Role
1. Click "Assign Role" on test user
2. ✅ **Expected**: Dropdown appears with available roles
3. Select a role (e.g., "KNOWLEDGE_STEWARD")
4. Click "Add"
5. ✅ **Expected**: Toast: "Role assigned successfully" (Phase 8a!)
6. ✅ **Expected**: Role badge appears in user's row
7. ✅ **Expected**: Role removed from dropdown (can't assign twice)

### Test 6: Roles Tab
1. Click "Roles" tab
2. ✅ **Expected**: List of all roles with descriptions:
   - ADMIN
   - KNOWLEDGE_STEWARD
   - USER
3. ✅ **Expected**: Each role shows name and display name

### Test 7: Configurations Tab
1. Click "Configurations" tab
2. ✅ **Expected**: Placeholder text: "Configuration management coming soon..."

### Test 8: Admin Access Control
1. Logout
2. Login as regular user (testuser / Test123!)
3. ✅ **Expected**: NO "Admin" link in header
4. Manually navigate to `http://localhost:5173/admin`
5. ✅ **Expected**: Redirect to `/chat` (access denied)

---

## 🎨 Step 5: Test Environment Toggle (Knowledge Steward)

### Test 1: Visibility for Admin
1. Login as admin (admin / Admin123!)
2. Go to chat
3. Look in chat header
4. ✅ **Expected**: See "Environment:" toggle (Production/Stage)
5. ✅ **Expected**: Production is green, Stage is yellow

### Test 2: Toggle Environment
1. Click "Stage" button
2. ✅ **Expected**: Stage turns yellow background
3. Click "Production" button
4. ✅ **Expected**: Production turns green background

### Test 3: Visibility for Knowledge Steward
1. Go to /admin
2. Assign "KNOWLEDGE_STEWARD" role to test user
3. Logout, login as testuser
4. ✅ **Expected**: See environment toggle in chat

### Test 4: Hidden for Regular Users
1. Go to /admin (as admin)
2. Remove all special roles from a user (leave only USER)
3. Logout, login as that user
4. ✅ **Expected**: NO environment toggle visible

---

## 🔍 Step 6: Integration Tests

### Test 1: Full Conversation Flow
1. Create new chat
2. Send 5 messages to AskAT&T
3. ✅ **Expected**: Conversation appears in sidebar after first message
4. ✅ **Expected**: Title = first message (truncated to 50 chars)
5. Switch to AskDocs
6. Select configuration
7. Send 3 messages
8. ✅ **Expected**: New conversation appears in sidebar
9. Click first conversation
10. ✅ **Expected**: All 5 messages load correctly
11. Continue that conversation
12. Send another message
13. ✅ **Expected**: Message added to existing conversation
14. ✅ **Expected**: Conversation moves to top of sidebar (updated_at)

### Test 2: Toast Coverage
1. Try each action and verify toast appears:
   - ✅ New chat → Info toast
   - ✅ Conversation loaded → Success toast
   - ✅ Copy message → Success toast
   - ✅ Feedback submitted → Success toast
   - ✅ Conversation deleted → Success toast
   - ✅ Failed config load → Error toast
   - ✅ No config selected → Error toast
   - ✅ Failed feedback → Error toast (disconnect backend to test)

### Test 3: Sidebar Responsiveness
1. Resize browser window to mobile size (<768px)
2. ✅ **Expected**: Sidebar starts closed
3. Click hamburger menu
4. ✅ **Expected**: Sidebar opens
5. Click anywhere outside sidebar
6. ✅ **Expected**: Sidebar closes (mobile behavior)

### Test 4: Empty State Variants
1. Create new chat → Empty state appears
2. Send message → Empty state disappears
3. Delete all conversations → Sidebar shows "No conversations yet"
4. Search for non-existent text → "No matching conversations"

---

## ⚠️ Step 7: Error Handling Tests

### Test 1: Backend Offline
1. Stop backend server (Ctrl+C in Terminal 1)
2. Try to send a message
3. ✅ **Expected**: Error toast (Phase 8a!)
4. ✅ **Expected**: No crash, app still usable

### Test 2: Invalid Token
1. Open DevTools → Application → Local Storage
2. Change `auth-storage` token to invalid value
3. Refresh page
4. ✅ **Expected**: Redirect to login (axios interceptor)

### Test 3: Configuration Access Denied
1. Login as user with only USER role
2. Note available configurations
3. Login as admin
4. Remove user's role from a configuration (via backend/database)
5. Login as user again
6. ✅ **Expected**: Configuration not in dropdown (filtered by RBAC)

---

## ✅ Success Criteria

### **Phase 8a: UI/UX Quick Wins**
- ✅ All toasts appear correctly (10+ different toast types)
- ✅ Copy button works with visual feedback
- ✅ Typing indicator shows before streaming
- ✅ Empty states guide users

### **Phase 6: Conversation History**
- ✅ Sidebar shows all conversations
- ✅ Grouped by date correctly
- ✅ Search works
- ✅ Delete works with confirmation
- ✅ Load conversation restores all messages
- ✅ Titles auto-generated
- ✅ Sidebar toggle works smoothly

### **Phase 7: Admin Panel**
- ✅ Admin link only visible to admins
- ✅ User table displays correctly
- ✅ Role assignment works
- ✅ Tabs switch correctly
- ✅ Access control works (non-admins redirected)
- ✅ Environment toggle visible to KS/Admin only

---

## 🐛 Known Issues to Check

1. **Conversation title truncation** - Should show "..." if > 50 chars
2. **Active conversation highlight** - Blue left border should persist
3. **Toast auto-dismiss** - Should disappear after ~5 seconds
4. **Copy button hover** - Should only show on hover, not on mobile tap
5. **Sidebar scroll** - Should scroll independently from chat

---

## 📊 Test Results Template

Use this to track your testing:

```
✅ Phase 8a: UI/UX Quick Wins
  ✅ Toast notifications (10/10 types working)
  ✅ Copy button
  ✅ Typing indicator
  ✅ Empty states

✅ Phase 6: Conversation History
  ✅ Sidebar display
  ✅ Date grouping
  ✅ Search
  ✅ Delete
  ✅ Load conversation
  ✅ Auto-titles
  ✅ Toggle sidebar

✅ Phase 7: Admin Panel
  ✅ Admin link visibility
  ✅ User table
  ✅ Assign roles
  ✅ Role display
  ✅ Access control
  ✅ Environment toggle

✅ Integration
  ✅ Full conversation flow
  ✅ Toast coverage
  ✅ Error handling
```

---

## 🎉 When All Tests Pass

**Congratulations!** You have a **fully functional, production-ready AI chat application** with:
- ✅ Complete conversation management
- ✅ Admin dashboard
- ✅ Professional UI/UX
- ✅ Role-based access control
- ✅ Real-time streaming
- ✅ Comprehensive error handling

**Next Steps**:
1. Optional: Implement Phase 8b/8c for additional polish
2. Replace MOCK services with real APIs
3. Deploy to staging
4. UAT testing
5. Production launch!

---

**Happy Testing! 🧪✨**

Report any bugs and we'll fix them immediately! 🚀
