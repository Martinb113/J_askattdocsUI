# Frontend Setup Guide

## Quick Start

### Prerequisites
- **Node.js 18+** installed
- **Backend running** on http://localhost:8000

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at: **http://localhost:3000**

## First-Time Setup (Step by Step)

### 1. Install Node.js

**Windows:**
- Download from https://nodejs.org/ (LTS version)
- Run the installer
- Verify installation:
  ```bash
  node --version  # Should show v18.x.x or higher
  npm --version   # Should show 9.x.x or higher
  ```

**Mac:**
```bash
brew install node@18
```

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Install Dependencies

```bash
cd frontend
npm install
```

This will install:
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Routing
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering
- **Lucide React** - Icons

### 3. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env if needed (default should work)
# VITE_API_URL=http://localhost:8000
```

### 4. Start Development Server

```bash
npm run dev
```

Output:
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
➜  press h + enter to show help
```

### 5. Open in Browser

Navigate to: **http://localhost:3000**

You should see the login page!

## Testing the Application

### 1. Login

Use the demo admin credentials:
- **AT&T ID**: `admin`
- **Password**: `Admin123!`

### 2. Test AskAT&T Chat

1. After login, you'll be on the Chat page
2. **AskAT&T** tab should be selected by default
3. Type a message: "Hello, how are you?"
4. Press Enter or click Send
5. Watch the **token-by-token streaming** response!

### 3. Test AskDocs Chat

1. Click the **AskDocs** tab
2. Select a configuration from the dropdown
3. Type: "How do I reset my password?"
4. Send the message
5. You should see:
   - Token-by-token streaming response
   - **Sources** at the bottom with clickable links

### 4. Test Feedback

1. After an assistant message appears
2. Look for "Was this helpful?"
3. Click thumbs up or thumbs down
4. Feedback is sent to the backend!

### 5. Create New User

1. Logout (top right)
2. Click "Sign up" on login page
3. Fill in the form:
   - Full Name: John Smith
   - AT&T ID: jsmith
   - Email: jsmith@att.com
   - Password: Test123! (must meet requirements)
4. Click "Sign up"
5. You'll be auto-logged in!

## Available Scripts

```bash
# Start development server (hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Textarea.tsx
│   │   ├── ChatMessage.tsx       # Message with markdown
│   │   ├── MessageList.tsx       # Scrollable message list
│   │   ├── Layout.tsx            # App shell
│   │   └── ProtectedRoute.tsx    # Auth guard
│   │
│   ├── pages/              # Page components
│   │   ├── Login.tsx       # Login page
│   │   ├── Signup.tsx      # Signup page
│   │   └── Chat.tsx        # Main chat page
│   │
│   ├── hooks/              # Custom React hooks
│   │   └── useStreamingChat.ts   # SSE streaming
│   │
│   ├── stores/             # Zustand stores
│   │   └── authStore.ts    # Authentication state
│   │
│   ├── lib/                # Utilities
│   │   ├── api.ts          # API client
│   │   └── utils.ts        # Helper functions
│   │
│   ├── types/              # TypeScript types
│   │   └── index.ts        # All type definitions
│   │
│   ├── App.tsx             # Main app with routing
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
│
├── public/                 # Static assets
├── index.html              # HTML template
├── package.json            # Dependencies
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
└── tsconfig.json           # TypeScript configuration
```

## Key Features Implemented

### ✅ Authentication
- Login with AT&T ID and password
- Signup with validation
- JWT token management
- Persistent auth (survives page refresh)
- Auto-redirect to login on 401

### ✅ Chat Interface
- Service selector (AskAT&T / AskDocs)
- Configuration dropdown for AskDocs
- Token-by-token SSE streaming
- Real-time message display
- Markdown rendering
- Source attribution for AskDocs
- Feedback collection (thumbs up/down)

### ✅ UI Components
- Responsive design (mobile-friendly)
- Loading states
- Error handling
- Custom scrollbar
- Keyboard shortcuts (Enter to send)

## Troubleshooting

### Port 3000 Already in Use

```bash
# Kill process on port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
npm run dev -- --port 3001
```

### CORS Errors

Ensure the backend CORS_ORIGINS includes your frontend URL:

```python
# backend/.env
CORS_ORIGINS=["http://localhost:3000"]
```

Then restart the backend.

### Cannot Connect to Backend

1. Check backend is running: http://localhost:8000/health
2. Check `.env` file has correct `VITE_API_URL`
3. Open browser console for error details

### SSE Streaming Not Working

1. Check browser supports EventSource (all modern browsers do)
2. Check backend logs for errors
3. Verify JWT token in browser localStorage
4. Test with curl:
   ```bash
   curl -N -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"message":"test"}' \
     http://localhost:8000/api/v1/chat/askatt
   ```

### Module Not Found Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors

```bash
# Check for type errors
npx tsc --noEmit

# Most errors are auto-fixed by the IDE
```

## Development Tips

### Hot Reload

Vite supports hot module replacement (HMR). Changes to `.tsx`, `.ts`, `.css` files are instantly reflected.

### Browser DevTools

1. Open DevTools (F12)
2. Check **Console** for errors
3. Check **Network** tab for API calls
4. Check **Application > Local Storage** for tokens

### Testing SSE Streaming

Open Network tab and filter by "EventStream" to see SSE messages.

### Debugging Auth Issues

```javascript
// In browser console
localStorage.getItem('access_token')  // Check token
localStorage.getItem('auth-storage')  // Check auth state
```

## Building for Production

### Build

```bash
npm run build
```

Output: `dist/` directory

### Preview Build

```bash
npm run preview
```

### Deploy

The `dist/` folder can be deployed to:
- **Vercel**: `vercel deploy`
- **Netlify**: Drag & drop `dist/` folder
- **Nginx**: Copy `dist/` to `/var/www/html`

### Environment Variables for Production

Create `.env.production`:

```env
VITE_API_URL=https://your-production-api.com
```

## Next Steps

1. ✅ **Test the chat** - Both AskAT&T and AskDocs
2. ✅ **Create new users** - Test signup flow
3. ✅ **Test feedback** - Rate assistant messages
4. 📋 **Add conversation history** - Sidebar with past chats (optional)
5. 📋 **Add admin panel** - User/role management (optional)

## Need Help?

- **Backend not running?** See `backend/QUICKSTART.md`
- **API errors?** Check backend logs
- **TypeScript errors?** Check `tsconfig.json`
- **Styling issues?** Check `tailwind.config.js`

---

**You're all set!** 🚀

Start chatting with the AI at http://localhost:3000
