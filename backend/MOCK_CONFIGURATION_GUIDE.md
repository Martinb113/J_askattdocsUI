# Mock Configuration Guide

This guide explains how the mock configuration system works for local development.

## Overview

The application uses mock implementations when `USE_MOCK_ASKDOCS=true` in `.env`. This allows developers to work without access to production APIs.

## Mock Domains and Configurations

### SD_International Domain

**Domain**: `SD_International`

**Configurations**:

1. **sim_wiki_con_v1v1**
   - Display Name: SIM Wiki Configuration v1.1
   - Description: Service Information Management wiki configuration for international teams
   - Version: 1.1
   - Team: SD International
   - Content Type: wiki
   - Region: global

2. **ois_wiki_com_v1v1**
   - Display Name: OIS Wiki Configuration v1.1
   - Description: Operational Information System wiki configuration for SD International
   - Version: 1.1
   - Team: SD International
   - Content Type: wiki
   - Region: global

### att_support Domain

**Domain**: `att_support`

**Configurations**:

1. **att_support_kb_v1**
   - Display Name: AT&T Support Knowledge Base v1
   - Description: Primary knowledge base for AT&T customer support
   - Version: 1.0
   - Team: Customer Support
   - Content Type: knowledge_base
   - Region: US

2. **att_support_faq_v2**
   - Display Name: AT&T Support FAQ v2
   - Description: Frequently asked questions for AT&T services
   - Version: 2.0
   - Team: Customer Support
   - Content Type: faq
   - Region: US

## Testing the Mock Endpoint

### Using the Test Script

```bash
cd backend
./venv/Scripts/python.exe test_fetch_config.py
```

### Using cURL

```bash
# 1. Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"attid": "admin", "password": "Admin123!"}'

# 2. Fetch configurations (replace TOKEN with actual token)
curl -X POST http://localhost:8000/api/v1/admin/configurations/fetch-by-domain \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "SD_International",
    "log_as_userid": "admin",
    "environment": "production"
  }'
```

## Adding New Mock Domains

To add new mock domains, edit `backend/app/services/askdocs_config.py`:

```python
mock_domain_configs = {
    "YOUR_DOMAIN_NAME": [
        {
            "config_key": "your_config_key_v1",
            "display_name": "Your Configuration v1",
            "description": "Description of your configuration",
            "version": "1.0",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "metadata": {
                "team": "Your Team",
                "content_type": "your_type",
                "region": "your_region"
            }
        }
    ]
}
```

## Role-Based Access Control

In production, configurations are filtered based on user roles. The admin can:

1. **Manually add domains** using the `/api/v1/admin/domains` endpoint
2. **Fetch configurations** from the external API using `/api/v1/admin/configurations/fetch-by-domain`
3. **Assign roles** to configurations to control which users can access them
4. **Users see only configurations** their roles have access to via `/api/v1/chat/configurations`

## Switching to Production API

To use the real production API instead of mocks:

1. Update `.env`:
   ```
   USE_MOCK_ASKDOCS=false
   ASKDOCS_CONFIG_API_STAGE=https://your-stage-api.com
   ASKDOCS_CONFIG_API_PRODUCTION=https://your-production-api.com
   ```

2. Restart the backend server

The endpoint will now call the real external API at `/admin/v2/list-config-by-domain`.

## API Specification

### Request Format

```json
{
  "domain": "string",
  "log_as_userid": "string",
  "environment": "production|stage"
}
```

### Response Format

```json
{
  "domain": "string",
  "environment": "string",
  "configurations": [
    {
      "config_key": "string",
      "display_name": "string",
      "description": "string",
      "version": "string",
      "is_active": boolean,
      "created_at": "ISO8601 timestamp",
      "metadata": {
        "team": "string",
        "content_type": "string",
        "region": "string"
      }
    }
  ],
  "total_count": number,
  "logged_as": "string",
  "timestamp": "ISO8601 timestamp"
}
```

## Notes

- Mock responses include realistic metadata for testing
- The timestamp in mock responses is dynamically generated
- Unknown domains will get a generic fallback configuration
- All mock configurations are marked as `is_active: true`
