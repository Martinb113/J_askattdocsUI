# AI Chat Application - Frontend

Modern React + TypeScript frontend for the AI Chat Application with Server-Sent Events (SSE) streaming support.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool (fast development)
- **Tailwind CSS** - Utility-first CSS
- **Zustand** - State management
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering for chat messages

## Quick Start

### Prerequisites

- Node.js 18+ installed
- Backend server running on http://localhost:8000

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: http://localhost:3000

### Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   └── ui/           # Base UI components (Button, Input, etc.)
│   ├── pages/            # Page components (Login, Signup, Chat, Admin)
│   ├── hooks/            # Custom React hooks
│   │   └── useStreamingChat.ts  # SSE streaming hook
│   ├── stores/           # Zustand state stores
│   │   └── authStore.ts  # Authentication state
│   ├── lib/              # Utilities and API client
│   │   ├── api.ts        # API client with axios
│   │   └── utils.ts      # Utility functions
│   ├── types/            # TypeScript type definitions
│   ├── index.css         # Global styles with Tailwind
│   ├── main.tsx          # App entry point
│   └── App.tsx           # Main app with routing
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Key Features

### 1. Authentication
- JWT-based authentication
- Login and signup pages
- Persistent auth state (localStorage)
- Automatic token refresh
- Protected routes

### 2. Real-Time Streaming Chat
- Server-Sent Events (SSE) for token-by-token streaming
- Support for both AskAT&T and AskDocs services
- Conversation persistence
- Message history

### 3. Role-Based Access
- Configuration filtering based on user roles
- Admin panel for user/role management
- Environment switcher (stage/production)

### 4. Chat Interface
- Markdown rendering for messages
- Source attribution for AskDocs responses
- Feedback collection (1-5 star rating)
- Conversation history sidebar

## Development

### Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

### Key Hooks

#### `useStreamingChat`
Custom hook for SSE streaming:

```typescript
import { useStreamingChat } from '@/hooks/useStreamingChat';

function ChatComponent() {
  const { sendMessage, message, isStreaming, sources } = useStreamingChat('askatt');

  const handleSend = async () => {
    await sendMessage({ message: 'Hello!' });
  };

  return (
    <div>
      {isStreaming && <p>Streaming: {message}</p>}
      {sources.map(source => <a href={source.url}>{source.title}</a>)}
    </div>
  );
}
```

#### `useAuthStore`
Zustand store for authentication:

```typescript
import { useAuthStore } from '@/stores/authStore';

function Component() {
  const { user, login, logout, isAuthenticated } = useAuthStore();

  return (
    <div>
      {isAuthenticated ? (
        <p>Welcome, {user?.full_name}!</p>
      ) : (
        <button onClick={() => login({ attid: 'user', password: 'pass' })}>
          Login
        </button>
      )}
    </div>
  );
}
```

### API Client

All API calls go through the `apiClient`:

```typescript
import apiClient from '@/lib/api';

// Login
const response = await apiClient.login({ attid: 'admin', password: 'Admin123!' });

// Get conversations
const conversations = await apiClient.getConversations('askatt');

// Get configurations (auto-filtered by roles)
const configs = await apiClient.getConfigurations();
```

## Pages

### Login (`/login`)
- AT&T ID and password authentication
- Demo credentials displayed
- Auto-redirect to chat on success

### Signup (`/signup`)
- New user registration
- Password strength validation
- Auto-login after signup

### Chat (`/chat`)
- Service selector (AskAT&T / AskDocs)
- Configuration selector (for AskDocs)
- Token-by-token streaming display
- Conversation history sidebar
- Message feedback UI

### Admin (`/admin`)
- User management
- Role assignment
- Configuration management
- Usage statistics

## Styling

### Tailwind CSS
All components use Tailwind utility classes:

```tsx
<div className="flex items-center justify-center min-h-screen bg-gray-50">
  <Button className="px-4 py-2 bg-primary-600 text-white rounded-lg">
    Click me
  </Button>
</div>
```

### Custom Styles
Additional styles in `src/index.css`:
- Custom scrollbar
- Markdown rendering styles
- Global typography

### Utility Function
Use `cn()` to merge Tailwind classes:

```tsx
import { cn } from '@/lib/utils';

<div className={cn('base-class', isActive && 'active-class', className)} />
```

## Testing

### Test Login Flow

1. Start frontend: `npm run dev`
2. Navigate to http://localhost:3000
3. Use demo credentials:
   - AT&T ID: `admin`
   - Password: `Admin123!`
4. You should be redirected to `/chat`

### Test Streaming Chat

1. Login as admin
2. Go to Chat page
3. Select "AskAT&T" service
4. Type a message and send
5. Watch token-by-token streaming

## Deployment

### Build Optimization

```bash
npm run build
```

Output: `dist/` directory

### Deploy to Vercel/Netlify

1. Connect GitHub repo
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variable: `VITE_API_URL=https://your-api.com`

### Deploy with Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Troubleshooting

### CORS Issues
If you see CORS errors, ensure the backend CORS_ORIGINS includes your frontend URL:

```python
# backend/.env
CORS_ORIGINS=["http://localhost:3000"]
```

### SSE Connection Fails
- Check backend is running
- Verify JWT token is valid (check localStorage)
- Check browser console for errors

### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Export conversation history
- [ ] Voice input for messages
- [ ] File upload for AskDocs
- [ ] Real-time collaboration
- [ ] WebSocket support (alternative to SSE)
- [ ] Progressive Web App (PWA)

## Support

For issues or questions:
1. Check backend logs
2. Check browser console
3. Verify API connectivity with `/health` endpoint
4. Review backend QUICKSTART.md

Happy coding! 🚀
