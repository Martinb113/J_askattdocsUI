# Changelog

All notable changes to the AI Chat Application will be documented in this file.

## [2025-10-21] - Streaming Fixes (Backend + Frontend)

### Fixed
- **Backend Streaming Error - Message Model Fields**
  - Fixed `TypeError: 'token_usage' is an invalid keyword argument for Message`
  - Root cause: `add_message()` was passing non-existent fields to Message model
  - Solution: Store token_usage and sources in `metadata_` field (JSONB)
  - Extract `total_tokens` for the `token_count` field
  - Location: `backend/app/services/conversation.py:141-197`

- **Backend Response Schema - Token Usage Extraction**
  - Fixed MessageResponse to read token_usage and sources from metadata
  - Added custom `from_orm()` method to extract nested metadata
  - Added `sources` field to MessageResponse schema
  - Location: `backend/app/schemas/chat.py:17-49`

- **Backend API Endpoint - Response Construction**
  - Fixed chat endpoints to use `MessageResponse.from_orm(msg)`
  - Ensures proper extraction of token_usage and sources
  - Location: `backend/app/api/v1/chat.py:363-366`

- **Frontend SSE Parsing - JSON Parse Error**
  - Fixed `SyntaxError: JSON.parse: unexpected non-whitespace character after JSON data at line 1 column 34`
  - Root cause: Frontend was parsing concatenated SSE events as single JSON string
  - Solution: Implemented proper SSE event buffering with `\n\n` delimiter
  - Added buffer to handle incomplete events across chunks
  - Location: `frontend/src/hooks/useStreamingChat.ts:89-176`

### Changed
- **SSE Event Processing**
  - Changed from single newline (`\n`) splitting to double newline (`\n\n`) splitting
  - Added buffer variable to accumulate incomplete events across chunks
  - Added `.trim()` to JSON strings before parsing
  - Added check to skip empty data lines

## [2025-10-20] - Response Format Fixes & Documentation Updates

### Added
- **Dual Response Format Support for AskAT&T**
  - Added support for real API format: `{"status": "success", "modelResult": {...}}`
  - Maintained backward compatibility with OpenAI-like format: `{"choices": [...]}`
  - Location: `backend/app/services/askatt.py:96-142`

- **Citations Parsing for AskDocs**
  - Added support for complex citations array from real API
  - Extracts meaningful titles from `metadata.captions.text` or `page_content`
  - Maintains backward compatibility with simple sources array
  - Location: `backend/app/services/askdocs.py:109-145`

### Changed
- **Updated ASKATT_INTEGRATION.md**
  - Documented dual response format support
  - Added response parsing logic details
  - Updated implementation notes

- **Updated ASKDOCS_API_INTEGRATION.md**
  - Documented citations array structure
  - Added citation parsing logic explanation
  - Updated response format examples

- **Updated DOCUMENTATION_INDEX.md**
  - Added "Recent Improvements" section
  - Updated documentation status table
  - Added changelog entries for 2025-10-20

- **Updated zzz_issues.md**
  - Marked streaming issues as FIXED
  - Marked response format issues as FIXED
  - Reorganized into FIXED and PENDING sections

### Fixed
- **Streaming Error Resolution**
  - Fixed backend response parsing to handle correct API formats
  - Resolved "TypeError: Error in input stream" issue
  - Backend now correctly extracts token usage from both response formats

- **AskAT&T Response Format Mismatch**
  - Service now handles both real API and mock service responses
  - Correctly extracts content from `modelResult.content` or `choices[0].message.content`
  - Properly parses token usage from `response_metadata.token_usage` or `usage`

- **AskDocs Citations Format Mismatch**
  - Service now parses complex citations array structure
  - Extracts meaningful source titles instead of raw IDs
  - Converts both citations and sources formats to unified frontend format

## [2025-10-18] - Initial Documentation & Security

### Added
- **Comprehensive Documentation**
  - Created `backend/README.md` - Complete backend setup guide
  - Created `backend/SECURITY.md` - Security guidelines and checklist
  - Created `DOCUMENTATION_INDEX.md` - Master documentation index
  - Created `backend/ASKATT_INTEGRATION.md` - AskAT&T API integration guide
  - Created `backend/ASKATT_TESTING.md` - Testing procedures and results
  - Created `backend/ASKDOCS_API_INTEGRATION.md` - AskDocs integration guide
  - Created `backend/MOCK_CONFIGURATION_GUIDE.md` - Mock configuration details

- **Security Infrastructure**
  - Created `.gitignore` to protect credentials
  - Updated `.env.example` with sanitized placeholders
  - Removed all real credentials from documentation

- **Azure AD OAuth2 Integration**
  - Implemented `backend/app/services/azure_ad.py`
  - Discovered and documented `/.default` scope requirement
  - Successfully tested token acquisition (general and domain scopes)

### Changed
- **Configuration Updates**
  - Updated all documentation to use placeholder values
  - Sanitized ASKATT_INTEGRATION.md
  - Sanitized ASKATT_TESTING.md

## [Earlier] - Mock Configuration for SD_International

### Added
- **Mock Domain Configurations**
  - Added SD_International domain with real team configurations
  - Included `sim_wiki_con_v1v1` - SIM Wiki Configuration v1.1
  - Included `ois_wiki_com_v1v1` - OIS Wiki Configuration v1.1
  - Location: `backend/app/services/askdocs_config.py`

## Known Issues

### Pending Implementation
- **Configuration Fetch API** (Issue #4 in zzz_issues.md)
  - Need to implement endpoint to fetch configurations from domain-services
  - Stage: `https://cast-southcentral-nprd-apim-02.azure-api.net/stage/domain-services/admin/list-config-by-domain`
  - Prod: `https://askatt-clientservices.web.att.com/domain-services/admin/list-config-by-domain`
  - Goal: Automatic population of configurations instead of manual entry

## Version Information

- **Backend**: FastAPI with PostgreSQL
- **Frontend**: React + TypeScript + Vite
- **Authentication**: JWT + Azure AD OAuth2
- **Mode**: Currently running in MOCK mode for development
- **Status**: Response format fixes complete, ready for production API testing

## Contributors

- AI Assistant (Claude Code)
- Development Team

---

**Note**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
