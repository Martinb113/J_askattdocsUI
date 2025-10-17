### Ask Docs Configuration Plan

 

This document captures how we will integrate **Ask Docs** as an additional LLM configuration option inside the settings sheet. The goal is to let a user supply the Ask Docs domain and configuration identifier, while keeping all sensitive credentials in environment variables.

 

---

 

#### 1. UX Flow

 

- Add an "Ask Docs" entry to the LLM provider selection UI. When chosen, prompt the user for:

  - Domain ID (e.g. `8970wikik`).

  - Config Version (e.g. `sim_wiki_con_v1v1`).

- The sheet should store these two values per user so the chat service can route requests through the Ask Docs endpoint.

- Credentials (client id, secret, tenant, scope, API base) will never be typed into the UI; they live in `.env`.

 

---

 

#### 2. Environment Variables

 

Add the following keys to `.env` (and document them in README):

 

```

ASKDOCS_CLIENT_ID=

ASKDOCS_CLIENT_SECRET=

ASKDOCS_TENANT_ID=

ASKDOCS_SCOPE=

ASKDOCS_API_BASE=https://askapi.stage.att.com

```

 

All sensitive values (client id/secret, tenant) stay server-side. The frontend only reads redacted capability flags from our API once the backend proxies Ask Docs.

 

---

 

#### 3. Token Retrieval (server-side only)

 

We will replace the inline sample script with a backend helper that exchanges client credentials for an access token using Azure AD. Pseudo steps:

 

1. `POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token`

2. Body parameters:

   - `client_id`, `client_secret` from env

   - `scope` from env (e.g. Ask Docs API scope)

   - `grant_type=client_credentials`

3. Cache the token until expiry (respect the `expires_in` value).

 

No credentials or tokens are printed or persisted in logs.

 

---

 

#### 4. Ask Docs Query API

 

Backend service obtains the bearer token and calls:

 

```

POST {ASKDOCS_API_BASE}/utility/chat

Authorization: Bearer <token>

Content-Type: application/json

 

{

  "domain": "<user-domain>",

  "config_version": "<user-config>",

  "query": "<question>"

}

```

 

Response data is streamed back to the frontend chat interface.

 

---

 

#### 5. Frontend Data Model Changes

 

- Extend `llm_providers` and `llm_models` mocks to allow a provider type of `ask_docs`.

- Persist user-supplied domain and config version in the mock DB under the Ask Docs model entry.

- Update `ConfigChecker` rules so Ask Docs entries validate domain + config values (API key not needed).

 

Data model deltas (mock & eventual Postgres):

 

Provider table additions:

- Add column `provider_type text NOT NULL DEFAULT 'custom'` where allowed values evolve to: `openai | anthropic | perplexity | ask_docs | custom` (enforce via enum in Postgres later; string in mock now).

 

Model table additions (only used when `provider_type='ask_docs'`):

- `ask_docs_domain text` (required for ask_docs models)

- `ask_docs_config_version text` (required)

- These two fields are ignored for other provider types.

 

Validation Rules:

1. If `provider_type=ask_docs`, `api_key` may be blank; backend proxy supplies token.

2. Both `ask_docs_domain` and `ask_docs_config_version` must be non-empty and <= 128 chars, alphanumeric plus `_ -`.

3. Display badge "Proxy Auth" instead of "API Key" status.

4. Config checker warns if user selects Ask Docs model but domain/config missing.

 

Service Layer Contract Adjustments:

- `llmConfigService.saveModel` / `updateModel` accept optional `ask_docs_domain`, `ask_docs_config_version`.

- Chat invocation path detects provider type; delegates to `askDocsService.query({ domain, configVersion, prompt })`.

 

UI Additions:

- In `ModelsTab`, when provider type = Ask Docs, show Domain + Config Version inputs instead of API Key.

- Add a filter pill in Overview to count Ask Docs models separately.

- In Config Checker, new issue types:

  - `askdocs_missing_domain`

  - `askdocs_missing_config`

  - `askdocs_invalid_chars`

- Add a small helper tooltip explaining these values are logical identifiers, not secrets.

 

---

 

#### 6. Security Notes

 

- Eliminate hard-coded secrets from docs; treat everything in `.env` as sensitive.

- Provide guidance for rotating secrets without redeploying the frontend (e.g. restart backend with new env values).

- Ensure logs redact token and domain/config details unless explicit debugging mode is enabled.

- Secret Rotation Policy:

  - Rotate `ASKDOCS_CLIENT_SECRET` quarterly or upon suspected compromise.

  - Keep two valid secrets briefly to avoid downtime; restart backend after update.

  - Document rotation in CHANGELOG (internal section) without exposing values.

- PII Handling:

  - User queries may contain sensitive information; do not persist full prompts by default until data retention policy defined.

  - If logging queries for debugging, hash or truncate after 256 chars.

- Failure Modes & Mitigations:

  - Auth failure: attempt refresh; if still failing, surface "Ask Docs authentication failed" banner and fall back to other models.

  - Rate limit (429): exponential backoff with jitter (250ms * 2^retry + random 0-100ms) up to 2 retries.

  - Network timeout (>15s): abort via `AbortController` and show retry CTA.

  - Partial response: if streaming supported later, close stream on malformed JSON and present partial text flagged as incomplete.

 

---

 

#### 7. Next Steps

 

1. Implement backend proxy that reads `.env` values and handles OAuth + Ask Docs requests.

2. Extend frontend configuration UI to add the Ask Docs provider type.

3. Wire chat service to use Ask Docs when the selected model belongs to that provider.

4. Document developer setup: required env vars, how to obtain credentials, test instructions.

 

---

 

#### 8. Backend Proxy Implementation Details

 

Service File: `src/services/askDocsService.ts` (to be created)

 

Responsibilities:

- Validate required env vars at module load; throw descriptive error if missing.

- Acquire + cache Azure AD token (in-memory) keyed by scope; refresh when <60s to expiry.

- Provide `query({ domain, configVersion, question, signal })` returning standardized response `{ answer, sources? }`.

- Rate limit outbound calls (simple token bucket: N per minute configurable via env, fallback 30/min).

- Map HTTP errors:

  - 400/404 => user-visible configuration error (suggest rechecking domain/config version)

  - 401/403 => internal auth refresh + single retry

  - 429 => exponential backoff (max 2 retries)

  - 5xx => surface generic transient error

 

Token Cache Structure:

```

interface TokenCache { token: string; expiresAt: number }

```

Stored in module scope; on retrieval if `Date.now() > expiresAt - 60000` fetch a new one.

 

Env Validation Checklist:

`ASKDOCS_CLIENT_ID, ASKDOCS_CLIENT_SECRET, ASKDOCS_TENANT_ID, ASKDOCS_SCOPE, ASKDOCS_API_BASE`.

 

Telemetry (optional future): count queries, failures, latency (wrap fetch & measure).

 

Error Redaction: never log full token or secrets; if logging headers, replace with `<redacted>`.

 

---

 

#### 9. Testing Strategy

 

Unit Tests (frontend):

- Validate form state for Ask Docs model (domain/config required, pattern rejects illegal chars).

- ConfigChecker: given mock models, emits proper issue types.

 

Unit Tests (backend):

- Token retrieval: returns cached token when fresh; refreshes when expiring.

- Error mapping: simulate 400, 401, 403, 429, 500 and assert correct retry / surface behavior.

- Rate limiting: exceed configured threshold and ensure additional calls are queued or rejected with clear error.

 

Integration Tests:

- End-to-end Ask Docs query using mocked fetch (inject fake token & response) returns normalized shape.

- Switching between OpenAI and Ask Docs models preserves conversation context but changes the request path.

 

UI / E2E (Playwright or Cypress future):

- Add Ask Docs model -> missing domain triggers validation -> fill -> success banner.

- Remove Ask Docs model -> chat fallback to previous provider.

 

Mocking Guidelines:

- Use deterministic token string `TEST_TOKEN` in tests; never real secrets.

- Fixture for Ask Docs response: `{ answer: "...", sources: [{ title, url }] }`.

 

Coverage Goals:

- 90% lines in `askDocsService.ts` (small file) focusing on edge branches (refresh, retries, failure mapping).

 

---

 

#### 10. Rollout & Migration

 

Feature Flag:

- Env flag `FEATURE_ASK_DOCS=true` toggles UI exposure; if false, provider type hidden and existing Ask Docs models filtered out.

 

Migration Steps:

1. Deploy backend proxy with flag disabled.

2. Add env secrets in staging; test via direct API call.

3. Enable flag in staging; run smoke tests.

4. Promote to production; initially keep flag off, then turn on gradually.

 

Backward Compatibility:

- Existing models without provider_type default to legacy behavior; new column nullable with default 'custom'.

- If user previously stored Ask Docs-like data in custom model, manual migration script can map.

 

Rollback Plan:

- Disable feature flag; no data loss (Ask Docs models remain but hidden). Optionally soft-delete those rows.

 

Seed Script (optional):

- Provide developer convenience script to insert a sample Ask Docs model with dummy domain/config when FEATURE_ASK_DOCS is on and user has none.

 

---

 

#### 11. Implementation Checklist

 

Backend:

- [ ] Create `src/services/askDocsService.ts` with token cache & query.

- [ ] Add env validation util or reuse existing config loader.

- [ ] Integrate into chat request pipeline (switch on provider_type).

 

Frontend:

- [ ] Extend provider/model types for ask_docs fields.

- [ ] Update `ModelsTab` form conditional inputs.

- [ ] Update `OverviewTab` and `ConfigChecker` to handle ask_docs.

- [ ] Add feature flag gating in UI (read from a config service or injected build-time var).

 

Database / Mock:

- [ ] Add provider_type, ask_docs_domain, ask_docs_config_version fields.

- [ ] Update persistence & seed logic for new fields.

 

Testing:

- [ ] Add unit tests for new validation.

- [ ] Add service tests for askDocsService (token, retries, errors).

 

Docs:

- [ ] Update README env var section.

- [ ] Add troubleshooting guide (401, 429 scenarios).

 

Observability (future):

- [ ] Add simple metrics wrapper.

APIs:

POST

/byod/domain-services/v2/chat-generativeai

Generative AI

This API enables free-form chat and advanced function/tool calling with OpenAI models.

Description: Enables free-form chat and advanced function/tool calling with OpenAI models.

Supports conversational prompts, tool use, and function-calling as defined by the OpenAI API.
Does not perform vector search or document retrieval — the input is sent directly to the specified OpenAI model.
Validates the requested model and input payload.
Returns the model’s response, including any function/tool call results, usage statistics, and relevant metadata.
Parameters: The payload describing the generative AI request. Expected fields include:

modelName (str): The model identifier to invoke (example: "gpt-4o").
modelPayload (object): The model input object. May include:
messages (List[dict] | null): For chat-capable models. message is { "role": "system|user|assistant", "content": "text" }
prompt (str | null): For legacy/completion-style models (e.g., text-ada-002) or single-shot prompts.
functions (array[object] | null): Function definitions for function-calling workflows (name, parameters, description).
tool_choice (object | null): Explicit tool selection metadata when multiple tools are provided.
tools (array[object] | null): Tool descriptors for external tool invocation (name, description, input schema).
seed (integer | null): Optional seed value to make sampling deterministic (provider-dependent).
temperature (number | null): Sampling temperature (0.0 - 2.0). Higher values produce more random outputs.
top_p (number | null): Nucleus sampling parameter; alternative to temperature.
max_tokens (integer | null): Maximum number of tokens to generate for the completion.
stop (array[string] | null): Sequence(s) where the model should stop generation.
presence_penalty (number | null): Penalize new tokens based on whether they appear in the text so far.
frequency_penalty (number | null): Penalize new tokens based on their existing frequency in the text so far.
best_of (integer | null): Number of completions to generate server-side and return the best (legacy).
logprobs (integer | null): Include log probabilities on the most likely tokens (legacy / provider-specific).
top_logprobs (integer | null): Include top logprobs for tokens (legacy / provider-specific).
response_format (object | null): Optional structured response formatting instructions (e.g., JSON schema)
Stage APIM Endpoint : https://cast-southcentral-nprd-apim-02.azure-api.net/stage/domain-services/chat-generativeai

Prod APIM Endpoint : https://askatt-clientservices.web.att.com/domain-services/chat-generativeai

Parameters

No parameters

Request body

 
  {

  "modelName": "gpt-4o",

  "modelPayload": {

    "max_tokens": 100,

    "messages": [

      {

        "content": "What's the weather like today?",

        "role": "user"

      }

    ],

    "stop": [

      "\n"

    ],

    "temperature": 0.7,

    "top_p": 0.9

  }

}

Responses

Code

Description

Links

200

Successful Response

Media type

Controls Accept header.

 
  "string"

No links

422

Validation Error

Media type

 
  {

  "detail": [

    {

      "loc": [

        "string",

        0

      ],

      "msg": "string",

      "type": "string"

    }

  ]

}

No links

POST

/byod/domain-services/v2/chat

Askattqna Chat

This API enables Retrieval-Augmented Generation (RAG) chat on the ATT knowledge base.

Description:

Accepts a user question and optional chat history, performs similarity search over the domain's vector index to retrieve relevant context, and invokes the configured LLM to generate an answer grounded in the retrieved content. Supports prompts, context override, image questions, metadata filters, and optional cache-ignore behavior.

Parameters:

domain (string) - Domain key/name for chat (example: "care")
version (string | null) - Configuration version; defaults to domain's defaultConfigVersion if omitted (example: "2025-01-01")
modelPayload (object) - Container for question, history, and control flags:
question (string)
history (array[object]) - chat history entries (optional)
prompt (string) - oOptional per-request instruction template to steer tone, format, or constraints. When AdvanceOptions.overwrite_prompt.enabled = true in the domain config, this value overrides the domain’s configured prompt for this request; otherwise it is ignored. May include placeholders like {question} and {context} that the service can fill before calling the LLM.
userIgnoreCache (boolean) - when true, bypass AI cache
askImage (boolean) - enable image-based QA (when supported)
filterBy (string | null) - additional filter expression
logAsUserID (string | null) - optional telemetry identity
filter (object | null) - Metadata-based filters for retrieval. Provide a map of field to list of values, e.g. {"Category":["value1","value2"]}. Ensure filterable fields are defined in the domain index.
Stage APIM Endpoint : https://cast-southcentral-nprd-apim-02.azure-api.net/stage/domain-services/chat

Prod APIM Endpoint : https://askatt-clientservices.web.att.com/domain-services/chat

Parameters

No parameters

Request body

 
  {

  "domain": "care",

  "version": "2025-01-01",

  "modelPayload": {

    "askImage": false,

    "filterBy": "",

    "history": [

      {

        "answer": "Your balance is $100.",

        "question": "What is my account balance?"

      }

    ],

    "logAsUserID": "user-1234",

    "question": "How do I reset my password?",

    "userIgnoreCache": false

  },

  "filter": {

    "Category": [

      "value1",

      "value2"

    ]

 }

}

Responses

Code

Description

Links

200

Successful Response

Media type

Controls Accept header.

 
  "string"

No links

422

Validation Error

Media type

 
  {

  "detail": [

    {

      "loc": [

        "string",

        0

      ],

      "msg": "string",

      "type": "string"

    }

  ]

}

No links

