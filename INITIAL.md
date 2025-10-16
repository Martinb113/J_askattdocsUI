# FEATURE: AI Chat Application with Token-Based Access (AskAT&T & AskDocs)

## Project Overview
This is a comprehensive AI chat application providing two distinct services:

### Service 1: AskAT&T
- Simple LLM prompt APIs for general question answering
- Direct AI interaction without domain-specific context
- OAuth2 authentication via Microsoft Azure AD

### Service 2: AskDocs (askattqna)
- Document-based question answering with domain-specific knowledge
- Multiple APIs for different domains (extensible architecture)
- Domain and configuration management via UI
- Users can select which domain to prompt from the interface
- OAuth2 authentication via Microsoft Azure AD

## Authentication Architecture
Both services use Azure AD OAuth2 authentication with the following configuration:
- **Auth Provider**: Microsoft Azure AD
- **Tenant ID**: e741d71c-c6b6-47b0-803c-0f3b32b07556
- **Client ID**: a1d886f8-c40b-465b-a7eb-0eec6f2a3998
- **Application Scope**: api://95273ce2-6fec-4001-9716-a209d398184f/.default
- **Domain QnA Scope**: api://95273ce2-6fec-4001-9716-a209d398184f/.DomainQnA
- **Grant Type**: client_credentials
- **Auth URL**: https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token

## Token-Based Access Control
To manage API usage and costs, the application implements a token-based payment system where users purchase tokens to access the AI services. Each API interaction consumes one token.

We want a PRP between 500 and 1000 lines and between 15-20 tasks in total.

## Frontend (frontend/ is the folder)

### Core Chat Interface
- Main chat interface supporting both AskAT&T and AskDocs services
- Service selector to switch between AskAT&T and AskDocs
- Domain configuration UI for AskDocs service:
  - Dropdown or selection interface to choose which domain to query
  - Domain settings management (add/edit/remove domains)
  - Domain-specific configuration options
- Azure AD OAuth2 authentication integration
  - Login/logout functionality
  - Token refresh handling
  - Secure storage of access tokens

### Token Management UI
- Page to view purchase options for agent tokens and purchase them
- Integration with Stripe payment flow for token purchases (changes will be needed on the frontend but we have to handle the purchase and redirect in the frontend)
- Success and failure pages after purchase completion
- Update to the user profile component to display the tokens available (fetched from the Supabase user record)
- Token usage history page to show past purchases and token consumption (fetched directly from Supabase in the frontend)
- Token balance display in the main chat interface (fetched directly from Supabase in the frontend)
- Display helpful error message when a message is rejected from the backend because no more tokens for the user

## Backend (backend_agent_api/ is the main folder and SQL in sql/)

### Authentication & Authorization
- Azure AD OAuth2 token validation middleware for all protected endpoints
- JWT token verification using Microsoft's public keys
- User session management and token refresh logic
- Integration between Azure AD user identity and Supabase user records

### Core AI Services
- **AskAT&T API**: Simple LLM prompt endpoint for general Q&A
- **AskDocs API**: Domain-specific document Q&A endpoints
  - Support for multiple domain configurations
  - Domain selection and routing logic
  - Extensible architecture for adding new domains

### Domain Management
- Domain configuration storage in Supabase
- CRUD operations for domain settings
- Domain-specific API routing
- Per-user domain access control (if needed)

### Token Management System
- The user table in Supabase (see sql/) will need to be updated to include a column for the tokens the user currently has
- A transactions table to track all token purchases and usage for audit purposes
- Stripe webhook endpoint to handle when tokens are purchased with proper signature verification and idempotency handling
- Token validation and deduction logic for all AI service endpoints
- The main API endpoints for interacting with the AI services need to check the user token count in Supabase and either reject the interaction or deduct a token

### API Endpoints Required:

#### Authentication Endpoints
- `POST /api/auth/login` - Exchange Azure AD token for application session
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Invalidate session

#### AI Service Endpoints
- `POST /api/askatt/chat` - AskAT&T general Q&A endpoint (requires token)
- `POST /api/askdocs/chat` - AskDocs domain-specific Q&A endpoint (requires token)
- `GET /api/domains` - List available domains for AskDocs
- `POST /api/domains` - Create new domain configuration (admin)
- `PUT /api/domains/:id` - Update domain configuration (admin)
- `DELETE /api/domains/:id` - Delete domain configuration (admin)

#### Token & Payment Endpoints
- `POST /api/create-payment-intent` - Create Stripe payment intent
- `POST /api/webhook/stripe` - Handle Stripe webhooks with signature verification
- `GET /api/user/tokens` - Get current user's token balance
- `GET /api/user/transactions` - Get user's token transaction history

All AI service endpoints must:
1. Validate Azure AD authentication token
2. Check rate limiting
3. Verify user has available tokens
4. Deduct token before processing request
5. Log transaction in transactions table

## Database Schema Updates

### Users Table (Updated)
- `id` (UUID, primary key)
- `azure_ad_id` (TEXT, unique) - Azure AD user object ID
- `email` (TEXT, unique)
- `display_name` (TEXT)
- `tokens` (INTEGER, default: 0) - Current token balance
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `last_login` (TIMESTAMP)

### Transactions Table (New)
Track all token purchases and usage for audit purposes:
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to users)
- `transaction_type` (ENUM: 'purchase', 'consumption')
- `amount` (INTEGER) - Tokens added (positive) or consumed (negative)
- `balance_after` (INTEGER) - Token balance after transaction
- `stripe_payment_intent_id` (TEXT, nullable) - For purchases
- `idempotency_key` (TEXT, unique, nullable) - Prevent duplicate processing
- `service_type` (TEXT, nullable) - 'askatt' or 'askdocs' for consumption
- `domain_id` (UUID, nullable) - For askdocs consumption
- `metadata` (JSONB) - Additional details about the transaction
- `created_at` (TIMESTAMP)

### Domains Table (New)
Store AskDocs domain configurations:
- `id` (UUID, primary key)
- `name` (TEXT, unique) - Domain identifier
- `display_name` (TEXT) - User-friendly name
- `description` (TEXT)
- `api_endpoint` (TEXT) - Backend API endpoint for this domain
- `configuration` (JSONB) - Domain-specific settings
- `is_active` (BOOLEAN, default: true)
- `created_by` (UUID, foreign key to users, nullable)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Supabase RLS Policies
- **Users table**: Users can read/update their own record
- **Transactions table**: Users can view their own transactions (look at existing table RLS setup for examples)
- **Domains table**: All authenticated users can read active domains; only admins can create/update/delete

## DOCUMENTATION
- Use the Archon MCP server to search the Supabase documentation (both JS and Python) and the Stripe documentation
- Search the web (supplemental search) for anything you need with Stripe, Supabase, or Azure AD OAuth2
- Azure AD OAuth2 authentication flow documentation
- Microsoft identity platform token validation
- JWT token verification best practices

## OTHER CONSIDERATIONS

### Authentication Setup
- Implement Azure AD OAuth2 authentication flow for both services
- Handle token refresh and expiration gracefully
- Store Azure AD user information (object ID, email, display name) in Supabase users table
- Create user record in Supabase on first login if it doesn't exist
- Secure token storage in frontend (HttpOnly cookies or secure localStorage)

### Domain Configuration
- AskDocs service needs UI for domain selection
- Domain configurations should be stored in Supabase domains table
- Each domain can have custom settings stored in JSONB configuration field
- Future extensibility: Allow adding new domains without code changes

### Stripe & Token Management
- Output a markdown document in planning/stripe-setup.md after the complete implementation that specifies what new environment variables need to be set (and make sure you add those to .env.example) for Stripe (both the backend and the frontend) and what other steps need to be completed for the setup in Stripe, including things like making the webhook
- The purchase page should have three options - 100 tokens, 250 tokens, and 600 tokens ($5, $10, and $20). These will be the purchase options set up in Stripe too
- Tokens do not expire - they are permanent once purchased
- Implement proper Stripe signature verification for webhook security
- Include idempotency handling to prevent duplicate token grants if webhooks are retried

### Database & Deployment
- Update the necessary SQL scripts in sql/ with the new user table columns (azure_ad_id, last_login), transactions table, and domains table
- Create a migration script for those who already have the DB set up
- Be sure to update the .env.example at the top level of the repo, the docker-compose.yml, and the Dockerfile for the frontend
- Keep the implementation simple but effective - we're building for a dev environment initially

### Security Considerations
- Validate Azure AD tokens on every protected endpoint
- Implement rate limiting per user to prevent abuse
- Secure webhook endpoints with proper signature verification
- Use HTTPS in production for all API calls
- Never expose client secrets in frontend code

## Environment Variables Needed

### Backend
```bash
# Azure AD OAuth2 Configuration
AZURE_AD_TENANT_ID=your-tenant-id-here
AZURE_AD_CLIENT_ID=your-client-id-here
AZURE_AD_CLIENT_SECRET=your-client-secret-here
AZURE_AD_SCOPE=api://your-api-scope-here/.default
AZURE_AD_DOMAIN_QNA_SCOPE=api://your-api-scope-here/.DomainQnA

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# AskAT&T & AskDocs Service Configuration
ASKATT_API_ENDPOINT=https://askatt-stage-api.example.com
ASKDOCS_API_BASE_ENDPOINT=https://askdocs-stage-api.example.com

# Application Configuration
JWT_SECRET=your-jwt-secret-for-session-tokens
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend
```bash
# Azure AD OAuth2 Configuration
VITE_AZURE_AD_TENANT_ID=your-tenant-id-here
VITE_AZURE_AD_CLIENT_ID=your-client-id-here
VITE_AZURE_AD_SCOPE=api://your-api-scope-here/.default
VITE_AZURE_AD_REDIRECT_URI=http://localhost:5173/auth/callback

# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Supabase Configuration (for direct frontend queries)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# Stripe Configuration
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Notes on Environment Variables
- **Never commit the actual secrets to version control** - use .env.example with placeholder values
- Azure AD credentials are for the AskATT-Stage API application
- The client secret should be rotated periodically for security
- Keep track of secret IDs for reference in your secure credential management system
- In production, use production Stripe keys (pk_live_... and sk_live_...)
- CORS allowed origins should be updated for production deployment

## Authentication Flow Details

### User Authentication Flow
1. **Frontend Login Initiation**
   - User clicks "Login" button
   - Frontend initiates Azure AD OAuth2 flow
   - User is redirected to Microsoft login page

2. **Azure AD Authentication**
   - User enters Microsoft credentials
   - Azure AD validates credentials
   - Azure AD redirects back to application with authorization code

3. **Token Exchange**
   - Frontend receives authorization code
   - Frontend calls backend `/api/auth/login` with the code
   - Backend exchanges code for access token with Azure AD
   - Backend validates the token and extracts user information

4. **User Record Creation/Update**
   - Backend checks if user exists in Supabase (by azure_ad_id)
   - If new user, create record with default 0 tokens
   - Update last_login timestamp
   - Return session token to frontend

5. **Session Management**
   - Frontend stores session token securely
   - Session token used for all subsequent API calls
   - Token includes user_id and expiration
   - Frontend refreshes token before expiration

### API Request Flow (with Token Deduction)
1. Frontend sends request to AI endpoint (AskAT&T or AskDocs)
2. Backend validates session token
3. Backend verifies Azure AD token is still valid
4. Backend checks rate limiting
5. Backend checks user has tokens available
6. If tokens available:
   - Deduct 1 token from user balance
   - Create consumption transaction record
   - Forward request to AI service (AskAT&T or AskDocs API)
   - Return AI response to frontend
7. If no tokens:
   - Return 402 Payment Required error
   - Frontend displays token purchase prompt

### Token Purchase Flow
1. User selects token package (100, 250, or 600 tokens)
2. Frontend calls `/api/create-payment-intent` with package selection
3. Backend creates Stripe payment intent
4. Frontend redirects to Stripe Checkout
5. User completes payment on Stripe
6. Stripe sends webhook to `/api/webhook/stripe`
7. Backend verifies webhook signature
8. Backend checks idempotency key to prevent duplicates
9. Backend adds tokens to user account
10. Backend creates purchase transaction record
11. Frontend redirects user to success page
12. User can now use AI services

## Implementation Priorities

### Phase 1: Authentication & Database Setup
1. Update database schema (users, transactions, domains tables)
2. Create SQL migration scripts
3. Implement Azure AD OAuth2 authentication on backend
4. Implement authentication UI on frontend (login/logout)
5. Test authentication flow end-to-end

### Phase 2: Core AI Service Integration
1. Implement AskAT&T chat endpoint
2. Implement AskDocs chat endpoint with domain routing
3. Create domain management CRUD endpoints
4. Build chat interface UI with service selector
5. Build domain configuration UI for AskDocs
6. Test both AI services without token gating

### Phase 3: Token Management System
1. Implement token check and deduction logic
2. Add token balance display in UI
3. Implement Stripe payment intent creation
4. Implement Stripe webhook handler
5. Build token purchase page UI
6. Create success/failure pages
7. Test token purchase and consumption flow

### Phase 4: Additional Features & Polish
1. Implement token usage history page
2. Add user profile with token balance
3. Implement proper error handling and user feedback
4. Add rate limiting
5. Security audit and testing
6. Documentation and deployment guides

## API Request/Response Examples

### Authentication
```json
// POST /api/auth/login
Request:
{
  "code": "azure_ad_authorization_code"
}

Response:
{
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "display_name": "John Doe",
    "tokens": 100
  }
}
```

### AskAT&T Chat
```json
// POST /api/askatt/chat
Request:
{
  "message": "What is the capital of France?"
}

Response:
{
  "response": "The capital of France is Paris.",
  "tokens_remaining": 99
}
```

### AskDocs Chat
```json
// POST /api/askdocs/chat
Request:
{
  "message": "What is the return policy?",
  "domain_id": "uuid-of-domain"
}

Response:
{
  "response": "Based on the documents, the return policy is...",
  "tokens_remaining": 98,
  "domain_name": "Customer Support"
}
```

### Token Purchase
```json
// POST /api/create-payment-intent
Request:
{
  "package": "100" // or "250" or "600"
}

Response:
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx"
}
```

## Testing Checklist
- [ ] Azure AD authentication flow works correctly
- [ ] User creation on first login
- [ ] Token balance displays correctly
- [ ] AskAT&T service responds to queries
- [ ] AskDocs service responds with domain selection
- [ ] Domain CRUD operations work
- [ ] Token deduction on each AI query
- [ ] API rejects requests when no tokens available
- [ ] Stripe payment flow completes successfully
- [ ] Webhook adds tokens after payment
- [ ] Idempotency prevents duplicate token grants
- [ ] Transaction history displays correctly
- [ ] Rate limiting works correctly
- [ ] All environment variables are documented
- [ ] .env.example is up to date
- [ ] Docker configuration is updated