# PRP: AI Chat Application - AskAT&T & AskDocs Integration

## Feature Goal
Build a modern AI chat application that provides role-based access to two distinct AI services: **AskAT&T** (general OpenAI chat) and **AskDocs** (domain-specific RAG chat). The application tracks user interactions, collects feedback for quality improvement, and manages multi-environment access (Stage/Production) for Knowledge Stewards. Users authenticate via simple credentials stored in PostgreSQL, while the application authenticates to external AI services via Azure AD OAuth2.

## Deliverable
A production-ready web application with:
- React/TypeScript frontend with streaming chat interface
- Python FastAPI backend with dual AI service integration
- PostgreSQL database with role-based access control
- Comprehensive conversation history and feedback collection
- Admin panel for user/role/configuration management
- Environment switcher for Knowledge Stewards (Stage/Production)

## Success Definition
- Users can signup with AT&TID, login, and chat with both services
- Streaming responses render token-by-token with proper markdown formatting
- Role-based configuration access works correctly (OIS sees only OIS configs, etc.)
- All conversations and feedback are persisted with full context (service, domain, config, environment)
- Knowledge Stewards can toggle between Stage and Production environments
- Token usage is logged for cost analysis (backend only, not user-facing)
- Admin can manage user roles and configuration access via UI

---

## Context & Research

### Required Knowledge
```yaml
docs:
  - name: "FastAPI - WebSocket & Streaming"
    url: "https://fastapi.tiangolo.com/advanced/websockets/"
    relevance: "Streaming AI responses to frontend"
    key_points: "Use StreamingResponse or WebSocket for token-by-token rendering"

  - name: "React - Server-Sent Events (SSE)"
    url: "https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events"
    relevance: "Frontend streaming implementation"
    key_points: "EventSource API for unidirectional streaming from backend"

  - name: "SQLAlchemy - Relationships & ORM"
    url: "https://docs.sqlalchemy.org/en/20/orm/relationships.html"
    relevance: "Many-to-many relationships for roles/configs"
    key_points: "Use association tables for User-Roles and Role-Configurations"

  - name: "Azure AD OAuth2 - Client Credentials Flow"
    url: "https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow"
    relevance: "Application-level authentication to external AI APIs"
    key_points: "POST to /oauth2/v2.0/token with client_id, client_secret, scope"

  - name: "JWT Authentication in FastAPI"
    url: "https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/"
    relevance: "User session management"
    key_points: "Use python-jose for JWT encoding/decoding, passlib for password hashing"

  - name: "React Markdown Rendering"
    url: "https://github.com/remarkjs/react-markdown"
    relevance: "Render AI responses with formatting"
    key_points: "Use react-markdown with syntax highlighting plugins"

patterns:
  - location: "PRPs/ai_docs/azure-ad-oauth2.md"
    pattern: "Token caching with expiration check"
    example: "Cache token in-memory, refresh when expires_in < 60 seconds"

  - location: "PRPs/ai_docs/stripe-integration.md"
    pattern: "Webhook signature verification"
    example: "N/A - no payment webhooks in this project"

gotchas:
  - issue: "Azure AD token caching must be server-side only"
    solution: "Never expose client_secret to frontend; cache tokens in backend memory/Redis"
    reference: "Microsoft security best practices"

  - issue: "Streaming responses require special CORS handling"
    solution: "Set proper headers: Access-Control-Allow-Origin, text/event-stream content-type"
    reference: "FastAPI StreamingResponse documentation"

  - issue: "PostgreSQL UUID generation requires extension"
    solution: "Enable uuid-ossp or use gen_random_uuid() in Postgres 13+"
    reference: "PostgreSQL UUID documentation"

  - issue: "Role-based filtering must happen in SQL, not Python"
    solution: "JOIN user_roles + role_configuration_access in query, don't filter in-memory"
    reference: "Performance best practice"

  - issue: "Environment switching changes API endpoint, not just query param"
    solution: "Backend must route to different ASKDOCS_API_BASE_URL based on environment field"
    reference: "ad_initial.md API endpoints"

examples:
  - url: "https://github.com/tiangolo/fastapi/discussions/4146"
    description: "FastAPI streaming with SSE"
    relevance: "Pattern for token-by-token streaming"

  - url: "https://github.com/vercel/next.js/tree/canary/examples/api-routes-rest"
    description: "Clean API route structure"
    relevance: "Organize FastAPI endpoints similarly"

project_context:
  - aspect: "Two-Layer Authentication"
    details: "Layer 1: App authenticates to Azure AD (client credentials). Layer 2: User authenticates to app (AT&TID + password)"
    implications: "Frontend never touches Azure credentials; backend proxies all AI API calls"

  - aspect: "Dual AI Services with Different Architectures"
    details: "AskAT&T = direct OpenAI chat (no RAG). AskDocs = RAG with vector search + sources"
    implications: "Different request payloads, response structures, and UI components"

  - aspect: "Domain → Configuration → Role Access Hierarchy"
    details: "1 Domain (currently), Multiple Configs, Many-to-many Role-Config mapping"
    implications: "Users see only configs their role(s) have access to; must filter at query time"

  - aspect: "Stage vs Production Environments"
    details: "Same database, different API endpoints; configurations tagged with environment column"
    implications: "Knowledge Stewards toggle environment in UI; backend routes to different URL"

  - aspect: "Feedback Granularity"
    details: "Per-message feedback (not per-conversation) with full context tracking"
    implications: "Each feedback record must link: user, message, conversation, service, domain, config, environment"

  - aspect: "Token Tracking = Cost Analysis Only"
    details: "No user-facing token balance or payment; purely backend logging for analytics"
    implications: "Log prompt/completion tokens from API responses; optionally calculate estimated cost"

  - aspect: "PMG Integration = Future Phase"
    details: "Development phase: manual signup. Production: validate AT&TID against PMG database"
    implications: "Design user table now to accommodate future PMG sync (external user ID, sync timestamp)"
```

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React/TS)                      │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Chat Interface │  │ Service Switch │  │ Config Selector  │  │
│  │  (Streaming)   │  │ AskAT&T/Docs   │  │ (Role-filtered)  │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Feedback UI    │  │ Conversation   │  │ Environment      │  │
│  │ (Thumbs +/-)   │  │ History        │  │ Switcher (KS)    │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓ HTTP/SSE
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI + Python)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Auth Layer: JWT validation, role extraction              │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌────────────────────┐         ┌──────────────────────────┐  │
│  │ AskAT&T Service    │         │ AskDocs Service          │  │
│  │ - Azure token mgmt │         │ - Azure token mgmt       │  │
│  │ - OpenAI chat      │         │ - RAG + vector search    │  │
│  │ - Streaming        │         │ - Sources extraction     │  │
│  └────────────────────┘         └──────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Conversation Manager: Store messages, track context      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Feedback Service: Link feedback to message/config/env    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL (Local Windows)                    │
│  Users, Roles, User_Roles, Domains, Configurations,             │
│  Role_Configuration_Access, Conversations, Messages, Feedback   │
└─────────────────────────────────────────────────────────────────┘
                            ↑
                   (Azure AD OAuth2)
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              External AI APIs (Azure AD Protected)               │
│  ┌─────────────────────┐      ┌──────────────────────────────┐ │
│  │ AskAT&T API         │      │ AskDocs API                  │ │
│  │ /chat-generativeai  │      │ /chat                        │ │
│  │ (Stage/Production)  │      │ (Stage/Production)           │ │
│  └─────────────────────┘      └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Technical Stack
```yaml
backend:
  framework: "FastAPI (latest stable)"
  language: "Python 3.11+"
  database: "PostgreSQL (local Windows installation)"
  orm: "SQLAlchemy 2.0+"
  auth: "JWT (python-jose) + bcrypt (passlib) for user auth; Azure AD OAuth2 for app auth"
  key_libraries:
    - "httpx (async HTTP client for external API calls)"
    - "pydantic (request/response validation)"
    - "uvicorn (ASGI server)"
    - "alembic (database migrations)"
    - "python-dotenv (environment variables)"

frontend:
  framework: "React 18 with TypeScript"
  build_tool: "Vite"
  styling: "Tailwind CSS + shadcn/ui components (optional)"
  state_management: "Zustand or React Context (lightweight)"
  key_libraries:
    - "react-markdown (markdown rendering)"
    - "react-syntax-highlighter (code blocks)"
    - "axios or fetch (HTTP client)"
    - "EventSource or custom hook for SSE streaming"

infrastructure:
  database: "Local PostgreSQL on Windows (psql, pgAdmin)"
  development: "localhost:8000 (backend), localhost:5173 (frontend)"
  future_production: "Cloud hosting (Azure, AWS) with managed PostgreSQL"

external_services:
  - "Azure AD (application OAuth2 authentication)"
  - "AskAT&T API (Stage & Production endpoints)"
  - "AskDocs API (Stage & Production endpoints)"
```

### Dependencies & Prerequisites
- [ ] PostgreSQL installed and running on Windows (version 13+)
- [ ] Python 3.11+ installed with pip/uv
- [ ] Node.js 18+ and npm/yarn installed
- [ ] Azure AD credentials obtained (tenant ID, client ID, client secret, scopes)
- [ ] Access to AskAT&T and AskDocs API endpoints (Stage URLs for testing)
- [ ] Understanding of React hooks, TypeScript, FastAPI async patterns

---

## Key Requirements & Clarifications

### Authentication Architecture (Critical)
```yaml
layer_1_application_auth:
  purpose: "Application authenticates to Azure AD to access external AI APIs"
  flow: "Client Credentials Grant (grant_type=client_credentials)"
  credentials: "AZURE_AD_CLIENT_ID, AZURE_AD_CLIENT_SECRET, AZURE_AD_TENANT_ID"
  scope: "api://95273ce2-6fec-4001-9716/.default (AskAT&T), .DomainQnA (AskDocs)"
  token_storage: "Backend in-memory cache with expiration tracking"
  user_visibility: "None - users never interact with Azure AD"

layer_2_user_auth:
  purpose: "Users authenticate to application to access features"
  flow: "Manual signup (AT&TID, email, password, role) → Login (AT&TID + password) → JWT session token"
  credentials: "Stored in PostgreSQL (password hashed with bcrypt)"
  token_storage: "Frontend (HttpOnly cookie or secure localStorage)"
  future_enhancement: "Validate AT&TID against PMG database; auto-assign roles from PMG"
```

### Dual AI Services (Critical)
```yaml
askatt_service:
  purpose: "General knowledge OpenAI chat (no domain-specific context)"
  api_endpoint: "POST /byod/domain-services/v2/chat-generativeai"
  stage_url: "https://cast-southcentral-nprd-apim-02.azure-api.net/stage/domain-services"
  production_url: "https://askatt-clientservices.web.att.com/domain-services"
  request_payload:
    modelName: "gpt-4o (or user-selectable)"
    modelPayload:
      messages: "[{role, content}, ...] (conversation history)"
      temperature: "0.7 (configurable)"
      max_tokens: "500 (configurable)"
  response_structure:
    response: "Generated text"
    usage: "{prompt_tokens, completion_tokens, total_tokens}"
  ui_elements: "Service selector, model dropdown (optional), temperature slider (optional)"

askdocs_service:
  purpose: "Domain-specific RAG chat with vector search and source attribution"
  api_endpoint: "POST /byod/domain-services/v2/chat"
  stage_url: "https://cast-southcentral-nprd-apim-02.azure-api.net/stage/domain-services"
  production_url: "https://askatt-clientservices.web.att.com/domain-services"
  request_payload:
    domain: "customer_care (from selected configuration)"
    version: "care_config_v1 (from selected configuration)"
    modelPayload:
      question: "User's message"
      history: "[{question, answer}, ...] (conversation history)"
      filter: "{Category: [values]} (optional metadata filters)"
      userIgnoreCache: "false (true for debugging)"
  response_structure:
    answer: "Generated text grounded in retrieved documents"
    sources: "[{title, url, snippet}, ...]"
    usage: "{prompt_tokens, completion_tokens, total_tokens}"
  ui_elements: "Service selector, domain dropdown, configuration dropdown (role-filtered), sources display"
```

### Role-Based Access Control (Critical)
```yaml
roles:
  - name: "OIS"
    access: "care_config_v1, care_config_v2 (production only)"
  - name: "SIM"
    access: "care_config_v1 (production only)"
  - name: "MANAGER"
    access: "Team configs + custom configs"
  - name: "ADMIN"
    access: "All configurations, admin panel"
  - name: "SME"
    access: "All knowledge domains"
  - name: "KNOWLEDGE_STEWARD"
    access: "Role-based configs + environment switcher (stage and production)"

access_control_flow:
  signup: "User selects role from dropdown (OIS/SIM initially)"
  query_time: "Backend JOINs user_roles → role_configuration_access → configurations → filters by user's roles"
  ui_filtering: "Frontend fetches accessible configurations via /api/configurations endpoint"
  authorization: "Before processing chat request, verify user has access to selected configuration"
```

### Environment Switching (Knowledge Stewards Only)
```yaml
environments:
  - name: "Stage"
    purpose: "Testing environment with test configurations and data"
    api_base: "ASKDOCS_API_BASE_URL_STAGE env variable"
    configurations: "Configurations with environment='stage'"
  - name: "Production"
    purpose: "Live environment with production configurations"
    api_base: "ASKDOCS_API_BASE_URL_PRODUCTION env variable"
    configurations: "Configurations with environment='production'"

implementation:
  ui_toggle: "Button/switch visible only to KNOWLEDGE_STEWARD role"
  state_management: "Frontend stores current environment in context/store"
  api_requests: "Include environment field in request payload"
  backend_routing: "Read environment from request → select appropriate API base URL → make request"
  data_separation: "All conversations/feedback tagged with environment column for analytics"
```

### Feedback Collection (Critical)
```yaml
granularity: "Per-message (each assistant response can receive feedback)"
rating_types: ["up", "down"]
ui_flow:
  - "Thumbs up/down buttons on each assistant message"
  - "On thumbs down: show comment textarea (optional)"
  - "Submit feedback → POST /api/feedback"
data_captured:
  - user_id: "Who provided feedback"
  - conversation_id: "Which conversation"
  - message_id: "Which specific message"
  - rating: "up or down"
  - comment: "Optional user explanation"
  - service_type: "askatt or askdocs"
  - domain_id: "NULL for AskAT&T, domain UUID for AskDocs"
  - configuration_id: "NULL for AskAT&T, config UUID for AskDocs"
  - environment: "stage or production"
analytics_use:
  - "Admin dashboard: aggregate positive/negative rates by service/config"
  - "Review negative feedback comments for quality improvement"
  - "Track which configurations have low satisfaction"
```

### Token Usage Logging (Non-User-Facing)
```yaml
purpose: "Cost analysis and capacity planning (not billing)"
capture_points: "After every AI API call (AskAT&T and AskDocs)"
data_logged:
  - user_id: "Who made the request"
  - conversation_id: "Context"
  - message_id: "Specific message"
  - service_type: "askatt or askdocs"
  - model_name: "gpt-4o, gpt-3.5-turbo, etc."
  - prompt_tokens: "From API response usage object"
  - completion_tokens: "From API response usage object"
  - total_tokens: "Sum of prompt + completion"
  - estimated_cost: "Optional (multiply tokens by model pricing)"
user_visibility: "None (backend logging only)"
admin_visibility: "Optional dashboard showing total consumption trends"
```

---

## Database Schema (Core Tables)

```yaml
users:
  columns:
    - id: "UUID PRIMARY KEY"
    - attid: "VARCHAR(50) UNIQUE NOT NULL (AT&T employee ID)"
    - email: "VARCHAR(255) UNIQUE NOT NULL"
    - password_hash: "VARCHAR(255) NOT NULL (bcrypt hashed)"
    - display_name: "VARCHAR(255)"
    - is_active: "BOOLEAN DEFAULT TRUE"
    - is_admin: "BOOLEAN DEFAULT FALSE"
    - created_at: "TIMESTAMP"
    - updated_at: "TIMESTAMP"
    - last_login: "TIMESTAMP"
  indexes: ["attid", "email"]

roles:
  columns:
    - id: "UUID PRIMARY KEY"
    - name: "VARCHAR(50) UNIQUE (OIS, SIM, MANAGER, etc.)"
    - display_name: "VARCHAR(100)"
    - description: "TEXT"
    - created_at: "TIMESTAMP"
  seed_data: ["OIS", "SIM", "MANAGER", "ADMIN", "SME", "KNOWLEDGE_STEWARD"]

user_roles:
  purpose: "Many-to-many: Users can have multiple roles"
  columns:
    - id: "UUID PRIMARY KEY"
    - user_id: "UUID REFERENCES users"
    - role_id: "UUID REFERENCES roles"
    - assigned_by: "UUID REFERENCES users (admin who assigned)"
    - assigned_at: "TIMESTAMP"
  constraints: ["UNIQUE(user_id, role_id)"]

domains:
  columns:
    - id: "UUID PRIMARY KEY"
    - domain_key: "VARCHAR(100) UNIQUE (e.g., 'customer_care')"
    - display_name: "VARCHAR(255)"
    - description: "TEXT"
    - is_active: "BOOLEAN DEFAULT TRUE"
    - created_at: "TIMESTAMP"
  seed_data: ["customer_care"]

configurations:
  purpose: "Configuration versions within a domain (e.g., care_config_v1)"
  columns:
    - id: "UUID PRIMARY KEY"
    - domain_id: "UUID REFERENCES domains"
    - config_key: "VARCHAR(100) (e.g., 'care_config_v1')"
    - display_name: "VARCHAR(255)"
    - description: "TEXT"
    - environment: "VARCHAR(20) DEFAULT 'production' (stage or production)"
    - is_active: "BOOLEAN DEFAULT TRUE"
    - metadata: "JSONB (additional config settings)"
    - created_at: "TIMESTAMP"
  constraints: ["UNIQUE(domain_id, config_key, environment)"]
  seed_data:
    - "customer_care | care_config_v1 | production"
    - "customer_care | care_config_v2 | production"
    - "customer_care | care_config_test | stage"

role_configuration_access:
  purpose: "Many-to-many: Which roles can access which configurations"
  columns:
    - id: "UUID PRIMARY KEY"
    - role_id: "UUID REFERENCES roles"
    - configuration_id: "UUID REFERENCES configurations"
    - granted_by: "UUID REFERENCES users (admin)"
    - granted_at: "TIMESTAMP"
  constraints: ["UNIQUE(role_id, configuration_id)"]
  seed_data:
    - "OIS → care_config_v1, care_config_v2"
    - "SIM → care_config_v1"

conversations:
  columns:
    - id: "UUID PRIMARY KEY"
    - user_id: "UUID REFERENCES users"
    - service_type: "VARCHAR(20) (askatt or askdocs)"
    - domain_id: "UUID REFERENCES domains (NULL for AskAT&T)"
    - configuration_id: "UUID REFERENCES configurations (NULL for AskAT&T)"
    - environment: "VARCHAR(20) (stage or production, NULL for AskAT&T)"
    - title: "VARCHAR(255) (auto-generated from first message)"
    - is_active: "BOOLEAN DEFAULT TRUE (soft delete)"
    - created_at: "TIMESTAMP"
    - updated_at: "TIMESTAMP"

messages:
  columns:
    - id: "UUID PRIMARY KEY"
    - conversation_id: "UUID REFERENCES conversations"
    - role: "VARCHAR(20) (user, assistant, system)"
    - content: "TEXT"
    - token_count: "INTEGER (for cost tracking)"
    - metadata: "JSONB (sources for AskDocs, model used, etc.)"
    - created_at: "TIMESTAMP"

feedback:
  columns:
    - id: "UUID PRIMARY KEY"
    - user_id: "UUID REFERENCES users"
    - conversation_id: "UUID REFERENCES conversations"
    - message_id: "UUID REFERENCES messages"
    - rating: "VARCHAR(10) CHECK (rating IN ('up', 'down'))"
    - comment: "TEXT (optional user explanation)"
    - service_type: "VARCHAR(20)"
    - domain_id: "UUID REFERENCES domains (NULL for AskAT&T)"
    - configuration_id: "UUID REFERENCES configurations (NULL for AskAT&T)"
    - environment: "VARCHAR(20)"
    - created_at: "TIMESTAMP"
  constraints: ["UNIQUE(user_id, message_id)"]

token_usage_log:
  purpose: "Cost tracking (optional, backend only)"
  columns:
    - id: "UUID PRIMARY KEY"
    - user_id: "UUID REFERENCES users"
    - conversation_id: "UUID REFERENCES conversations"
    - message_id: "UUID REFERENCES messages"
    - service_type: "VARCHAR(20)"
    - model_name: "VARCHAR(100)"
    - prompt_tokens: "INTEGER"
    - completion_tokens: "INTEGER"
    - total_tokens: "INTEGER"
    - estimated_cost: "DECIMAL(10, 6) (optional)"
    - created_at: "TIMESTAMP"

audit_log:
  purpose: "Track admin actions (role assignments, config access grants)"
  columns:
    - id: "UUID PRIMARY KEY"
    - user_id: "UUID REFERENCES users (who performed action)"
    - action: "VARCHAR(100) (ASSIGN_ROLE, GRANT_CONFIG_ACCESS, etc.)"
    - entity_type: "VARCHAR(50) (USER, ROLE, CONFIGURATION)"
    - entity_id: "UUID"
    - details: "JSONB"
    - created_at: "TIMESTAMP"
```

---

## API Endpoints (High-Level)

```yaml
authentication:
  - "POST /api/auth/signup": "Create user account (attid, email, password, role)"
  - "POST /api/auth/login": "Authenticate user, return JWT token"
  - "POST /api/auth/refresh": "Refresh expired JWT token"
  - "POST /api/auth/logout": "Invalidate session"

user_management:
  - "GET /api/users/me": "Get current user profile + accessible configurations"
  - "GET /api/roles": "List available roles (for signup dropdown or admin)"

configurations:
  - "GET /api/domains": "List all active domains"
  - "GET /api/configurations": "List configurations accessible to current user (filtered by role)"
    query_params: ["environment (stage/production)", "domain_id"]

chat_services:
  - "POST /api/askatt/chat": "Chat with AskAT&T (general OpenAI)"
    payload: ["conversation_id (optional)", "message", "model (optional)", "temperature (optional)"]
    response: "Streaming SSE or JSON response with message, token usage"
  
  - "POST /api/askdocs/chat": "Chat with AskDocs (RAG)"
    payload: ["conversation_id (optional)", "configuration_id", "message", "environment", "filters (optional)"]
    response: "Streaming SSE or JSON response with answer, sources, token usage"

conversations:
  - "GET /api/conversations": "List user's conversation history"
    query_params: ["service_type", "limit", "offset"]
  - "GET /api/conversations/{id}": "Get full conversation with all messages"
  - "DELETE /api/conversations/{id}": "Soft delete conversation"

feedback:
  - "POST /api/feedback": "Submit feedback on message"
    payload: ["message_id", "conversation_id", "rating (up/down)", "comment (optional)"]
  - "GET /api/feedback/stats": "Get feedback analytics (admin only)"

admin:
  - "POST /api/admin/users/{user_id}/roles": "Assign role to user"
  - "DELETE /api/admin/users/{user_id}/roles/{role_id}": "Revoke role from user"
  - "POST /api/admin/roles/{role_id}/configurations": "Grant config access to role"
  - "DELETE /api/admin/roles/{role_id}/configurations/{config_id}": "Revoke config access"
```

---

## User Interaction Flows

### Flow 1: New User Signup & First Chat
```
1. User navigates to app → Landing page
2. Click "Sign Up"
   → Form: AT&TID, Email, Password, Display Name, Role dropdown (OIS/SIM)
   → Submit → Backend creates user, assigns role
3. Redirect to Login → Enter AT&TID + Password
   → Backend validates, returns JWT token
   → Frontend stores token, redirects to chat
4. Chat interface loads:
   → Service selector defaults to "AskDocs"
   → Configuration dropdown shows only accessible configs (OIS → v1, v2)
   → User selects care_config_v1
5. User types: "How do I reset my password?"
   → Frontend: POST /api/askdocs/chat with configuration_id
   → Backend: Validates JWT, checks role access, calls AskDocs API
   → Streams response with sources
6. Frontend renders response token-by-token + expandable source cards
7. User clicks thumbs up → Feedback submitted
```

### Flow 2: Switching Services
```
1. User in AskDocs conversation → Has chat history
2. Click "Switch to AskAT&T"
   → Frontend saves conversation state
   → Hides configuration selector
   → Starts new conversation
3. User asks: "Explain quantum entanglement"
   → Frontend: POST /api/askatt/chat
   → Backend: Calls AskAT&T generative AI endpoint
   → Streams response (no sources)
4. User provides feedback: Thumbs down + "Too technical"
   → Feedback logged with service_type='askatt', domain_id=NULL
```

### Flow 3: Knowledge Steward Environment Switching
```
1. Knowledge Steward logs in → Environment switcher visible (Stage/Production)
2. Defaults to Production
3. User clicks "Switch to Stage"
   → Frontend updates environment state
   → Configuration dropdown filters to environment='stage'
   → Backend routes requests to ASKDOCS_API_BASE_URL_STAGE
4. User tests new configuration in stage → Provides feedback
5. User switches back to Production → Sees production configs
```

### Flow 4: Admin Managing Access
```
1. Admin logs in → "Admin Panel" visible in navigation
2. Navigate to "Configuration Access Management"
   → UI shows matrix: Rows=Roles, Columns=Configurations, Checkboxes=Access
3. Admin checks "SIM → care_config_v2"
   → Frontend: POST /api/admin/roles/{role_id}/configurations
   → Backend: Creates entry in role_configuration_access, logs in audit_log
4. SIM users immediately see care_config_v2 in dropdown
```

---

## Validation Strategy

### Level 1: Syntax & Code Quality
```bash
# Backend
cd backend_agent_api
ruff check --fix .
mypy app/

# Frontend
cd frontend
npm run lint
npm run type-check
```

### Level 2: Unit Tests
```bash
# Backend
pytest tests/ -v --cov=app

# Frontend
npm run test
```

### Level 3: Integration Tests
```bash
# Start backend
uvicorn app.main:app --reload

# Test endpoints (use Postman, curl, or automated tests)
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"attid":"ab12345","email":"test@example.com","password":"Test123!","display_name":"Test User","role":"OIS"}'

curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"attid":"ab12345","password":"Test123!"}'

# Test chat streaming (should see token-by-token)
curl -X POST http://localhost:8000/api/askdocs/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"configuration_id":"uuid","message":"Test question","environment":"production"}'
```

### Level 4: Manual Testing Checklist
```yaml
authentication:
  - [ ] "Signup with duplicate AT&TID fails gracefully"
  - [ ] "Login with wrong password shows error"
  - [ ] "JWT expiration triggers refresh flow"

chat_functionality:
  - [ ] "AskAT&T streaming works smoothly (token-by-token rendering)"
  - [ ] "AskDocs sources display correctly (expandable cards)"
  - [ ] "Service switcher preserves conversation history"
  - [ ] "Markdown/code blocks render properly"

role_based_access:
  - [ ] "OIS user sees only OIS configurations"
  - [ ] "SIM user sees only SIM configurations"
  - [ ] "Unauthorized config access returns 403"

environment_switching:
  - [ ] "Knowledge Steward sees environment toggle"
  - [ ] "Non-KS users don't see environment toggle"
  - [ ] "Stage environment routes to stage API endpoint"
  - [ ] "Conversations tagged with correct environment"

feedback:
  - [ ] "Thumbs up submits successfully"
  - [ ] "Thumbs down shows comment textarea"
  - [ ] "Duplicate feedback prevented (unique constraint)"
  - [ ] "Feedback appears in admin dashboard"

admin:
  - [ ] "Admin can assign roles to users"
  - [ ] "Admin can grant config access to roles"
  - [ ] "Actions logged in audit_log table"
  - [ ] "Non-admin users get 403 on admin endpoints"

conversation_management:
  - [ ] "Conversation history loads and displays correctly"
  - [ ] "Resuming conversation includes previous context"
  - [ ] "Soft delete removes conversation from UI but preserves in DB"
```

---

## Environment Variables

### Backend (backend_agent_api/.env)
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/askdocs_db

# JWT Authentication
JWT_SECRET=your-secure-random-secret-256-bit
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Azure AD OAuth2 (Application-Level)
AZURE_AD_TENANT_ID=e741d71c-c6b6-xxxx
AZURE_AD_CLIENT_ID=a1d886f8-c40b-xxxx
AZURE_AD_CLIENT_SECRET=your-client-secret-here
AZURE_AD_SCOPE=api://95273ce2-6fec-4001-9716/.default
AZURE_AD_DOMAIN_QNA_SCOPE=api://95273ce2-6fec-4001-9716/.DomainQnA

# AskAT&T API
ASKATT_API_BASE_URL_STAGE=https://cast-southcentral-nprd-apim-02.azure-api.net/stage/domain-services
ASKATT_API_BASE_URL_PRODUCTION=https://askatt-clientservices.web.att.com/domain-services

# AskDocs API
ASKDOCS_API_BASE_URL_STAGE=https://cast-southcentral-nprd-apim-02.azure-api.net/stage/domain-services
ASKDOCS_API_BASE_URL_PRODUCTION=https://askatt-clientservices.web.att.com/domain-services

# Default Models
DEFAULT_ASKATT_MODEL=gpt-4o
DEFAULT_ASKDOCS_MODEL=gpt-4o

# Logging
LOG_LEVEL=INFO
```

### Frontend (frontend/.env)
```bash
# Backend API
VITE_API_BASE_URL=http://localhost:8000

# App Metadata
VITE_APP_NAME=AskAI Chat
VITE_APP_VERSION=1.0.0
```

---

## Implementation Phases (High-Level)

```yaml
phase_1_foundation:
  tasks: ["PostgreSQL setup", "Database schema creation", "Seed data", "User signup/login", "JWT middleware"]
  acceptance: "Users can signup with AT&TID + role, login, receive JWT token"

phase_2_askatt_integration:
  tasks: ["Azure AD OAuth client", "AskAT&T service", "Chat endpoint", "Conversation storage", "Basic chat UI"]
  acceptance: "Users can chat with AskAT&T, responses stored in DB"

phase_3_askdocs_integration:
  tasks: ["AskDocs service", "Configuration selector UI", "Role-based filtering", "Sources display"]
  acceptance: "Users can chat with AskDocs, see sources, filtered by role"

phase_4_streaming_ux:
  tasks: ["SSE streaming backend", "Frontend SSE consumer", "Token-by-token rendering", "Markdown formatting"]
  acceptance: "Responses stream smoothly with formatting"

phase_5_feedback:
  tasks: ["Feedback UI (thumbs +/-)", "Feedback API", "Admin dashboard"]
  acceptance: "Users can provide feedback, admins see analytics"

phase_6_admin_environment:
  tasks: ["Admin panel", "Role/config management", "Environment switcher", "Audit logging"]
  acceptance: "Admins manage access, KS switch environments"

phase_7_polish_test:
  tasks: ["Unit tests", "Integration tests", "Error handling", "Documentation", "Deployment guide"]
  acceptance: "All tests pass, documentation complete"
```

---

## Success Metrics

```yaml
technical_metrics:
  - "API response time < 2s (p95)"
  - "Streaming latency < 500ms (first token)"
  - "Database query time < 100ms (p95)"

user_engagement_metrics:
  - "Messages per user per session"
  - "Conversation length (messages per conversation)"
  - "Service usage ratio (AskAT&T vs AskDocs)"

quality_metrics:
  - "Positive feedback rate > 75%"
  - "Negative feedback with comments > 80%"
  - "Configuration access error rate < 1%"

cost_metrics:
  - "Average tokens per message (AskAT&T vs AskDocs)"
  - "Total token consumption per day"
  - "Estimated monthly API costs"
```

---

## Known Limitations & Future Enhancements

### Current Limitations (MVP)
- Manual user signup (no PMG integration yet)
- Single domain (customer_care only)
- Simple role assignment (no role hierarchy)
- No conversation search/filter
- No export functionality

### Future Enhancements (Post-MVP)
```yaml
pmg_integration:
  - "Validate AT&TID against PMG database"
  - "Auto-sync user roles from PMG"
  - "Scheduled sync job"

advanced_features:
  - "Voice input (speech-to-text)"
  - "Document visualization (embedded images/PDFs from sources)"
  - "Web search augmentation"
  - "CopilotKit integration"
  - "Multi-language support (i18n)"

analytics:
  - "Dashboard for token usage trends"
  - "User engagement metrics (session duration, retention)"
  - "Configuration popularity"
  - "Sentiment analysis on feedback comments"

performance:
  - "Response caching for common questions"
  - "Database query optimization (materialized views)"
  - "CDN for frontend assets"
  - "WebSocket connection pooling"
```

---

## References & Resources

### Primary Documentation
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- SQLAlchemy: https://docs.sqlalchemy.org/en/20/
- Azure AD OAuth2: https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow
- PostgreSQL: https://www.postgresql.org/docs/

### Implementation Examples
- FastAPI streaming: https://github.com/tiangolo/fastapi/discussions/4146
- React markdown: https://github.com/remarkjs/react-markdown
- JWT auth FastAPI: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

### Project-Specific Context
- `ad_initial.md`: AskDocs API specifications and configuration details
- `PRPs/ai_docs/azure-ad-oauth2.md`: Azure AD integration patterns
- `CLAUDE.md`: PRP methodology and validation requirements

---

## Final Validation Checklist

### Functionality
- [ ] All user flows work end-to-end
- [ ] Role-based access control enforced at DB and API level
- [ ] Streaming responses render correctly
- [ ] Feedback collection works for both services
- [ ] Environment switching routes to correct API endpoints

### Security
- [ ] Passwords hashed with bcrypt (cost factor 12+)
- [ ] JWT tokens signed and validated
- [ ] Azure AD client secret never exposed to frontend
- [ ] SQL injection prevented (parameterized queries)
- [ ] CORS configured correctly

### Code Quality
- [ ] All functions have docstrings
- [ ] Type hints used throughout (Python & TypeScript)
- [ ] No hardcoded secrets
- [ ] Error handling for all API calls
- [ ] Logging configured (no PII in logs)

### Documentation
- [ ] README with setup instructions
- [ ] .env.example with all required variables
- [ ] API documentation (Swagger/OpenAPI)
- [ ] User guide for chat interface
- [ ] Admin guide for access management

### Testing
- [ ] Unit tests > 80% coverage
- [ ] Integration tests for critical flows
- [ ] Manual testing checklist complete
- [ ] Performance benchmarks meet targets

---

## "No Prior Knowledge" Test

✅ **This PRP passes if an AI agent with no prior project knowledge can**:
1. Understand the dual-service architecture (AskAT&T vs AskDocs)
2. Implement two-layer authentication (app OAuth + user JWT)
3. Build role-based configuration access with many-to-many relationships
4. Integrate both external AI APIs with streaming
5. Create feedback collection system with full context tracking
6. Implement environment switching for Knowledge Stewards
7. Validate all implementations using provided test cases

**Confidence Score**: 9/10 - Comprehensive context, clear requirements, executable validation steps. Minor risk: streaming implementation details may need iteration for optimal UX.

---

**Document Version**: 2.0 (PRP Format)  
**Last Updated**: October 16, 2025  
**Status**: Ready for Implementation  
**Estimated Implementation Time**: 6-8 weeks (7 phases)
