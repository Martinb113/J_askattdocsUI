## ✅ FIXED ISSUES (2025-10-20)

### 1. ✅ AskAT&T Response Format Mismatch - FIXED
**Status**: RESOLVED
**Fix Location**: `backend/app/services/askatt.py:96-142`
**Solution**: Added dual response format support
- Primary: Real API format `{"status": "success", "modelResult": {...}}`
- Fallback: OpenAI-like format `{"choices": [...]}`

### 2. ✅ AskDocs Citations Format Mismatch - FIXED
**Status**: RESOLVED
**Fix Location**: `backend/app/services/askdocs.py:109-145`
**Solution**: Added citations parsing with dual format support
- Primary: Citations array with metadata and captions
- Fallback: Simple sources array
- Extracts meaningful titles from `metadata.captions.text` or `page_content`

### 3. ✅ Streaming Error - RESOLVED
**Previous Error**: "Failed to send message: TypeError: Error in input stream"
**Status**: RESOLVED
**Root Cause**: Backend was trying to use invalid `token_usage` field in Message model
**Solution**: Backend response parsing updated to handle correct response formats

---

## ⚠️ PENDING ISSUES

### 4. ⚠️ Configuration Management - NEEDS IMPLEMENTATION
**Status**: PENDING
**Issue**: Configuration setup is difficult and requires manual entry
**Planned Solution**: Implement API to fetch configurations from domain-services

**Original notes**:
"plus I am not sure why to setup configuation so dificult and currently doesnt not reflect what I would expect to be populated via using those APIs Bellow - that was plan from the start, then we will be puling this list so I dont have to manually add it one by one."

**API Details for Implementation**:
This API is used to get a list of configuration versions for a specific domain.

Description:

 

Retrieves configuration version entries for the provided domain from the domainConfiguration collection in Cosmos DB.

Parameters:

 

    domain (str): Domain key/name for listing configurations.

    log_as_userid (str | null): Optional user id to override logging identity.

 

Stage APIM Endpoint : https://cast-southcentral-nprd-apim-02.azure-api.net/stage/domain-services/admin/list-config-by-domain

 

Prod APIM Endpoint : https://askatt-clientservices.web.att.com/domain-services/admin/list-config-by-domain

 

curl -X 'POST' \

  'https://askapi.stage.att.com/byod/domain-services/admin/v2/list-config-by-domain' \

  -H 'accept: application/json' \

  -H 'Authorization: eyJ0eXAiOiJKV1QiLCJhb' \

  -H 'Content-Type: application/json' \

  -d '{

  "domain": "8970wikik",

  "log_as_userid": "attid"

}'

 

Response body

 

  {

    "_id": "8970wikik-sd_config_v3",

    "domain": "8970wikik",

    "version": "sd_config_v3",

    "domainName": "SD_International",

    "created_on": "2024-11-28T09:09:25.479Z"

  },

  {

    "_id": "8970wikik-sim_wiki_con_v1v1",

    "domain": "8970wikik",

    "version": "sim_wiki_con_v1v1",

    "domainName": "SD_International",

    "created_on": "2024-11-28T09:09:25.479Z"

  },

  {

    "_id": "8970wikik-ois_wiki_con_v1v1",

    "domain": "8970wikik",

    "version": "ois_wiki_con_v1v1",

    "domainName": "SD_International",

    "created_on": "2024-11-28T09:09:25.479Z"

  },

 

    "_id": "8970wikik-sim_wiki_con_v2v1",

    "domain": "8970wikik",

    "version": "sim_wiki_con_v2v1",

    "domainName": "SD_International",

    "created_on": "2024-11-28T09:09:25.479Z"

 

AsKAT&T Response:

{"domainName": "GenerativeAI", "modelName": "gpt-4o", "modelPayload": {"messages": [{"role": "user", "content": [{"type": "text", "text": "Tell me joke"}]}], "max_completion_tokens": 800}}

 

C:\ProgramData\anaconda3\Lib\site-packages\urllib3\connectionpool.py:1099: InsecureRequestWarning: Unverified HTTPS request is being made to host 'cso.proxy.att.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings

  warnings.warn(

 

{"status":"success","modelResult":{"content":"Sure, here's a joke for you:\n\nWhy don't skeletons fight each other?\n\nThey don't have the guts!","additional_kwargs":{"refusal":null},"response_metadata":{"token_usage":{"completion_tokens":22,"prompt_tokens":41,"total_tokens":63,"completion_tokens_details":{"accepted_prediction_tokens":0,"audio_tokens":0,"reasoning_tokens":0,"rejected_prediction_tokens":0},"prompt_tokens_details":{"audio_tokens":0,"cached_tokens":0}},"model_name":"gpt-4o-2024-08-06","system_fingerprint":"fp_cbf1785567","id":"chatcmpl-CS8BX3g3suYXcSt4KgegFZVekhZLi","service_tier":"default","finish_reason":"stop","logprobs":null,"content_filter_results":{}},"type":"ai","name":null,"id":"run--288accea-56ba-47cf-801b-1a6d4a82ef31-0","example":false,"tool_calls":[],"invalid_tool_calls":[],"usage_metadata":{"input_tokens":41,"output_tokens":22,"total_tokens":63,"input_token_details":{"audio":0,"cache_read":0},"output_token_details":{"audio":0,"reasoning":0}}}}

None

 

Ask DOcs response(Structure):

{

  "type": "object",

  "properties": {

    "response": { "type": "string" },

    "citations": {

      "type": "array",

      "items": {

        "type": "object",

        "properties": {

          "id": { "type": "string" },

          "metadata": {

            "type": "object",

            "properties": {

              "source": { "type": "string" },

              "chunk_id": { "type": "integer" },

              "captions": {

                "type": "object",

                "properties": {

                  "text": { "type": "string" },

                  "highlights": { "type": "string" }

                },

                "required": ["text"],

                "additionalProperties": true

              },

              "answers": { "type": ["string", "null"] }

            },

            "required": ["source"],

            "additionalProperties": true

          },

          "page_content": { "type": "string" },

          "type": { "type": "string" },

          "aisearch_score": { "type": "number" },

          "aisearch_reranker_score": { "type": "number" }

        },

        "required": ["id", "metadata"],

        "additionalProperties": true

      }

    },

    "usage": {

      "type": "object",

      "properties": {

        "total_tokens": { "type": "number" },

        "prompt_tokens": { "type": "number" },

        "prompt_tokens_cached": { "type": "number" },

        "completion_tokens": { "type": "number" },

        "reasoning_tokens": { "type": "number" },

        "successful_requests": { "type": "integer" },

        "similarity_search_seconds": { "type": "number" },

        "build_context_seconds": { "type": "number" },

        "llm_call_seconds": { "type": "number" },

        "cosmos_call_seconds": { "type": "number" },

        "init_app_ctx_seconds": { "type": "number" }

      },

      "additionalProperties": true

    },

    "question": { "type": "string" },

    "refactor_question": { "type": ["string", "null"] },

    "chat_history": { "type": ["array", "null"] },

    "aicache": { "type": "boolean" },

    "total_latency": { "type": "number" }

  },

  "required": ["response", "citations", "question"],

  "additionalProperties": true

}