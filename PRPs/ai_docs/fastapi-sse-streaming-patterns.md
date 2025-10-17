# FastAPI Server-Sent Events (SSE) Streaming Patterns for AI Chat Applications

## Overview

This document provides comprehensive guidance on implementing Server-Sent Events (SSE) streaming with FastAPI for AI chat applications, specifically for token-by-token streaming from OpenAI-style APIs.

## Official Documentation URLs

### FastAPI Core Documentation
- **StreamingResponse**: https://fastapi.tiangolo.com/advanced/custom-response/
- **CORS Configuration**: https://fastapi.tiangolo.com/tutorial/cors/
- **Behind a Proxy**: https://fastapi.tiangolo.com/advanced/behind-a-proxy/

### Third-Party Libraries
- **sse-starlette GitHub**: https://github.com/sysid/sse-starlette
- **sse-starlette PyPI**: https://pypi.org/project/sse-starlette/
- **pydantic-to-typescript**: https://pypi.org/project/pydantic-to-typescript/

### Community Resources
- **Client Disconnect Handling**: https://github.com/fastapi/fastapi/discussions/7572
- **Streaming Issues**: https://stackoverflow.com/questions/75740652/fastapi-streamingresponse-not-streaming-with-generator-function
- **OpenAI Streaming**: https://stackoverflow.com/questions/79042708/how-to-forward-openais-stream-response-using-fastapi-in-python
- **Nginx SSE Config**: https://serverfault.com/questions/801628/for-server-sent-events-sse-what-nginx-proxy-configuration-is-appropriate

---

## 1. Core Imports and Setup

### Essential Imports

```python
# FastAPI core
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# OpenAI client
from openai import AsyncOpenAI

# Standard library
import asyncio
import json
from typing import AsyncGenerator, Optional

# Optional: For production SSE implementation
from sse_starlette import EventSourceResponse, ServerSentEvent
```

### Application Initialization with Lifespan

```python
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, cleanup on shutdown."""
    # Initialize OpenAI client
    clients["openai"] = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    yield
    # Cleanup
    await clients["openai"].close()

app = FastAPI(lifespan=lifespan)
clients = {}
```

---

## 2. CORS Configuration for SSE

### Complete CORS Setup

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Define allowed origins (NEVER use ["*"] with credentials)
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Explicit origins required for credentials
    allow_credentials=True,             # Enable cookies/auth headers
    allow_methods=["*"],                # Allow all HTTP methods
    allow_headers=["*"],                # Allow all headers
    expose_headers=["X-Request-ID"],    # Optional: expose custom headers
    max_age=600,                        # Preflight cache duration (seconds)
)
```

### CORS Configuration Parameters

| Parameter | Purpose | Default | Notes |
|-----------|---------|---------|-------|
| `allow_origins` | List of permitted origins | Required | Cannot be `["*"]` when `allow_credentials=True` |
| `allow_credentials` | Enable cookies/auth headers | `False` | Requires explicit origin list |
| `allow_methods` | HTTP methods allowed | `["GET"]` | Use `["*"]` for all methods |
| `allow_headers` | Request headers supported | `[]` | Use `["*"]` for all headers |
| `expose_headers` | Response headers accessible to browsers | `[]` | List specific headers to expose |
| `max_age` | Browser cache duration for preflight | `600` | In seconds |

### CORS Critical Constraints

**When `allow_credentials=True`:**
- Origins MUST be explicitly listed (no wildcards)
- Methods MUST be explicitly listed (no wildcards in production)
- Headers MUST be explicitly listed (no wildcards in production)

---

## 3. Basic SSE Endpoint Setup

### Method 1: Using StreamingResponse (Built-in)

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def event_stream():
    """Basic async generator for SSE."""
    for i in range(10):
        # SSE format: "data: content\n\n"
        yield f"data: Message {i}\n\n"
        await asyncio.sleep(0.5)

@app.get("/stream")
async def stream_endpoint():
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
```

### Method 2: Using sse-starlette (Production-Ready)

```python
from sse_starlette import EventSourceResponse
import asyncio

async def event_generator():
    """Generator yielding structured events."""
    for i in range(10):
        # Yield as dictionary - sse-starlette handles formatting
        yield {
            "event": "message",
            "data": f"Event {i}",
            "id": str(i),
            "retry": 15000,  # Reconnection timeout (ms)
        }
        await asyncio.sleep(1)

@app.get("/stream")
async def stream_endpoint(request: Request):
    return EventSourceResponse(
        event_generator(),
        ping=15,  # Send ping every 15 seconds
    )
```

### SSE Event Format

```
event: event_type
data: event content
id: unique_event_id
retry: 15000

```

**Key Rules:**
- Each field is on a new line
- Format: `field_name: field_value`
- Events are separated by double newlines (`\n\n`)
- `data:` field is required
- `event:`, `id:`, and `retry:` are optional

---

## 4. Async Generator for Token-by-Token Streaming

### OpenAI Streaming Pattern (Modern AsyncOpenAI Client)

```python
from openai import AsyncOpenAI
from typing import AsyncGenerator

client = AsyncOpenAI(api_key="your-api-key")

async def stream_openai_response(
    messages: list[dict],
    model: str = "gpt-3.5-turbo"
) -> AsyncGenerator[str, None]:
    """
    Stream OpenAI chat completion token-by-token.

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: OpenAI model identifier

    Yields:
        Token content as strings
    """
    try:
        # Create streaming chat completion
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.7,
        )

        # Iterate over response chunks
        async for chunk in response:
            # Extract content from delta
            content = chunk.choices[0].delta.content
            if content:
                yield content

    except Exception as e:
        # Yield error as SSE event
        yield f"event: error\ndata: {str(e)}\n\n"
```

### FastAPI Endpoint with OpenAI Streaming

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    messages: list[dict]
    model: str = "gpt-3.5-turbo"
    stream: bool = True

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream OpenAI chat completion responses."""

    async def generate():
        async for token in stream_openai_response(
            messages=request.messages,
            model=request.model
        ):
            # Format as SSE
            yield f"data: {json.dumps({'token': token})}\n\n"

        # Send completion event
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
```

### Alternative: Accumulative Streaming Pattern

```python
async def stream_openai_accumulative(
    messages: list[dict]
) -> AsyncGenerator[str, None]:
    """Stream with accumulated content (useful for UI updates)."""

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
    )

    accumulated = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            accumulated += content
            # Yield full accumulated response
            yield accumulated
```

---

## 5. Error Handling Patterns

### Error Handling Wrapper for Generators

```python
from typing import AsyncGenerator
from openai import RateLimitError, APIError

async def stream_with_error_handling(
    generator: AsyncGenerator[str, None]
) -> AsyncGenerator[str, None]:
    """Wrap generator with comprehensive error handling."""
    try:
        async for chunk in generator:
            yield chunk

    except asyncio.CancelledError:
        # Client disconnected
        print("Client disconnected during streaming")
        # Don't yield anything - connection is closed

    except RateLimitError as e:
        error_msg = e.body.get("message", "OpenAI API rate limit exceeded")
        yield f"event: error\ndata: {json.dumps({'error': error_msg})}\n\n"

    except APIError as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': 'An unexpected error occurred'})}\n\n"
        print(f"Streaming error: {e}")
```

### Using Error Handler in Endpoint

```python
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream with error handling."""

    async def generate():
        generator = stream_openai_response(
            messages=request.messages,
            model=request.model
        )

        async for token in stream_with_error_handling(generator):
            yield f"data: {json.dumps({'token': token})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### Timeout Handling

```python
import async_timeout

async def stream_with_timeout(
    messages: list[dict],
    timeout_seconds: int = 30
) -> AsyncGenerator[str, None]:
    """Stream with timeout protection."""
    try:
        async with async_timeout.timeout(timeout_seconds):
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
            )

            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

    except asyncio.TimeoutError:
        yield "event: error\ndata: Request timeout\n\n"
```

---

## 6. Client Disconnect Handling

### Method 1: Using request.is_disconnected()

```python
from fastapi import Request

@app.get("/stream")
async def stream_endpoint(request: Request):
    """Handle client disconnects gracefully."""

    async def generate():
        for i in range(1_000_000):
            # Check if client disconnected
            if await request.is_disconnected():
                print(f"Client disconnected after {i} events")
                break

            yield f"data: Event {i}\n\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### Method 2: Using asyncio.CancelledError

```python
async def generate_with_cancellation():
    """Generator that handles cancellation."""
    try:
        for i in range(1_000_000):
            yield f"data: Event {i}\n\n"
            await asyncio.sleep(0.1)  # Must have await point

    except asyncio.CancelledError:
        print("Stream cancelled by client disconnect")
        # Cleanup resources here
        raise  # Re-raise to properly close connection
```

### Method 3: Using sse-starlette with Disconnect Detection

```python
from sse_starlette import EventSourceResponse

@app.get("/stream")
async def stream_endpoint(request: Request):
    """EventSourceResponse with disconnect detection."""

    async def event_generator():
        events_sent = 0
        try:
            while events_sent < 100:
                # Check disconnect status
                if await request.is_disconnected():
                    print(f"Client disconnected after {events_sent} events")
                    break

                yield {
                    "event": "message",
                    "data": f"Event {events_sent}",
                    "id": str(events_sent)
                }

                events_sent += 1
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            print("Stream cancelled")

    return EventSourceResponse(
        event_generator(),
        ping=15  # Keep connection alive
    )
```

### Complete Example with All Patterns

```python
@app.post("/chat/stream")
async def chat_stream_complete(request: Request, chat_request: ChatRequest):
    """Complete streaming endpoint with all best practices."""

    async def generate():
        try:
            response = await client.chat.completions.create(
                model=chat_request.model,
                messages=chat_request.messages,
                stream=True,
            )

            token_count = 0
            async for chunk in response:
                # Check for client disconnect
                if await request.is_disconnected():
                    print(f"Client disconnected after {token_count} tokens")
                    break

                content = chunk.choices[0].delta.content
                if content:
                    token_count += 1
                    yield f"data: {json.dumps({'token': content})}\n\n"

            # Send completion event
            yield f"event: done\ndata: {json.dumps({'tokens': token_count})}\n\n"

        except asyncio.CancelledError:
            print("Stream cancelled by client")

        except Exception as e:
            error_message = f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            yield error_message

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
```

---

## 7. Common Gotchas and Solutions

### Gotcha 1: Browser Buffering with text/plain

**Problem:** Browsers buffer ~1445 bytes of `text/plain` for MIME sniffing.

**Solution:**
```python
# Option 1: Use text/event-stream
return StreamingResponse(
    generator(),
    media_type="text/event-stream"
)

# Option 2: Add X-Content-Type-Options header
return StreamingResponse(
    generator(),
    media_type="text/plain",
    headers={"X-Content-Type-Options": "nosniff"}
)
```

### Gotcha 2: Blocking Operations in Async Generators

**Problem:** Using `time.sleep()` in `async def` generator blocks the event loop.

**Solution:**
```python
# WRONG: Blocks event loop
async def bad_generator():
    for i in range(10):
        yield f"data: {i}\n\n"
        time.sleep(1)  # BLOCKS!

# CORRECT Option 1: Use asyncio.sleep
async def good_generator_async():
    for i in range(10):
        yield f"data: {i}\n\n"
        await asyncio.sleep(1)  # Non-blocking

# CORRECT Option 2: Use sync generator for blocking ops
def good_generator_sync():
    for i in range(10):
        yield f"data: {i}\n\n"
        time.sleep(1)  # OK in sync generator
```

### Gotcha 3: Middleware Breaking Streaming

**Problem:** GzipMiddleware and logging middleware can buffer responses.

**Solution:**
```python
# Option 1: Disable middleware for streaming endpoints
@app.get("/stream")
async def stream_endpoint():
    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Content-Encoding": "identity"}  # Prevent compression
    )

# Option 2: Configure middleware to skip streaming
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Don't compress small responses
)
```

### Gotcha 4: Nginx Buffering

**Problem:** Nginx buffers responses by default, breaking SSE.

**Solution:**
```python
# Add header in FastAPI response
headers = {
    "X-Accel-Buffering": "no",  # Disable nginx buffering
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
}

return StreamingResponse(
    generator(),
    media_type="text/event-stream",
    headers=headers
)
```

**Nginx Configuration:**
```nginx
location /stream {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    # Don't set proxy_buffering off globally
    # Use X-Accel-Buffering header instead
}
```

### Gotcha 5: Client-Side Testing Issues

**Problem:** `requests.iter_lines()` waits for line breaks.

**Solution:**
```python
# WRONG: Buffers until newline
import requests
response = requests.get("http://localhost:8000/stream", stream=True)
for line in response.iter_lines():
    print(line)

# CORRECT: Stream by chunks
import requests
response = requests.get("http://localhost:8000/stream", stream=True)
for chunk in response.iter_content(chunk_size=None):
    print(chunk)

# BETTER: Use httpx for async
import httpx
async with httpx.AsyncClient() as client:
    async with client.stream("GET", "http://localhost:8000/stream") as response:
        async for chunk in response.aiter_text():
            print(chunk)
```

### Gotcha 6: Missing Await Points in Async Generators

**Problem:** `asyncio.CancelledError` not caught without await points.

**Solution:**
```python
# WRONG: No await points
async def bad_generator():
    for i in range(100):
        yield f"data: {i}\n\n"
        # No await - cancellation won't work!

# CORRECT: Regular await points
async def good_generator():
    for i in range(100):
        yield f"data: {i}\n\n"
        await asyncio.sleep(0)  # Minimal await point
```

### Gotcha 7: Not Handling Empty Content

**Problem:** OpenAI streams include chunks with no content.

**Solution:**
```python
async for chunk in response:
    content = chunk.choices[0].delta.content
    # ALWAYS check for None/empty content
    if content:
        yield f"data: {content}\n\n"
    # Skip if content is None or empty
```

---

## 8. Nginx Reverse Proxy Configuration

### Application-Level Headers (Critical)

```python
# Add these headers in your FastAPI response
headers = {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",  # Most important for nginx
    "Connection": "keep-alive",
}

return StreamingResponse(
    generator(),
    media_type="text/event-stream",
    headers=headers
)
```

### Nginx Configuration for SSE

```nginx
location /stream {
    proxy_pass http://localhost:8000;

    # Essential for SSE
    proxy_http_version 1.1;
    proxy_set_header Connection "";

    # Forward client headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Timeout settings for long-lived connections
    proxy_connect_timeout 7d;
    proxy_send_timeout 7d;
    proxy_read_timeout 7d;

    # Don't set proxy_buffering off globally
    # Let X-Accel-Buffering header control it per-response
}
```

### Key Nginx Settings Explained

| Setting | Value | Purpose |
|---------|-------|---------|
| `proxy_http_version` | `1.1` | Required for persistent connections |
| `proxy_set_header Connection` | `""` | Maintain persistent connection |
| `X-Accel-Buffering` | `no` | Disable buffering (set in app) |
| `proxy_buffering` | Don't set | Let header control it |
| `proxy_read_timeout` | `7d` | Prevent timeout on long streams |

---

## 9. TypeScript Integration

### Generating TypeScript Types from Pydantic

**Installation:**
```bash
pip install pydantic-to-typescript
```

**Usage:**
```python
# models.py
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str = "gpt-3.5-turbo"
    stream: bool = True

class ChatResponse(BaseModel):
    token: str
    finish_reason: str | None = None
```

**Generate TypeScript:**
```bash
# CLI
pydantic2ts --module models --output ./frontend/types.ts

# Or in Python
from pydantic2ts import generate_typescript_defs

generate_typescript_defs("models", "./frontend/types.ts")
```

**Generated TypeScript:**
```typescript
// types.ts
export interface ChatMessage {
    role: string;
    content: string;
}

export interface ChatRequest {
    messages: ChatMessage[];
    model?: string;
    stream?: boolean;
}

export interface ChatResponse {
    token: string;
    finish_reason?: string | null;
}
```

### Client-Side SSE Consumer (TypeScript/React)

```typescript
import { useEffect, useState } from 'react';

interface StreamMessage {
    token: string;
}

export function useChatStream(messages: ChatMessage[]) {
    const [response, setResponse] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const startStream = async () => {
        setIsStreaming(true);
        setResponse('');
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages,
                    model: 'gpt-3.5-turbo',
                    stream: true,
                }),
            });

            if (!response.body) {
                throw new Error('No response body');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        try {
                            const parsed: StreamMessage = JSON.parse(data);
                            setResponse(prev => prev + parsed.token);
                        } catch (e) {
                            console.error('Failed to parse:', data);
                        }
                    } else if (line.startsWith('event: error')) {
                        const errorLine = lines[lines.indexOf(line) + 1];
                        if (errorLine?.startsWith('data: ')) {
                            const errorData = JSON.parse(errorLine.slice(6));
                            setError(errorData.error);
                        }
                    }
                }
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setIsStreaming(false);
        }
    };

    return { response, isStreaming, error, startStream };
}
```

### Using EventSource API (Alternative)

```typescript
function streamWithEventSource(messages: ChatMessage[]) {
    // Encode request as URL params (GET only)
    const params = new URLSearchParams({
        messages: JSON.stringify(messages),
    });

    const eventSource = new EventSource(
        `http://localhost:8000/chat/stream?${params}`
    );

    eventSource.onmessage = (event) => {
        const data: StreamMessage = JSON.parse(event.data);
        console.log('Received:', data.token);
    };

    eventSource.addEventListener('error', (event) => {
        const data = JSON.parse((event as MessageEvent).data);
        console.error('Error:', data.error);
    });

    eventSource.addEventListener('done', () => {
        console.log('Stream complete');
        eventSource.close();
    });

    // Cleanup
    return () => eventSource.close();
}
```

---

## 10. Complete Production-Ready Example

### Backend Implementation

```python
"""
Complete FastAPI SSE streaming implementation for AI chat.
"""
import asyncio
import contextlib
import json
import os
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI, RateLimitError, APIError
from pydantic import BaseModel, Field


# ============================================================================
# Models
# ============================================================================

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str = "gpt-3.5-turbo"
    stream: bool = True
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)

class StreamToken(BaseModel):
    token: str
    finish_reason: Optional[str] = None


# ============================================================================
# Application Setup
# ============================================================================

clients = {}

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    # Startup
    clients["openai"] = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    print("OpenAI client initialized")

    yield

    # Shutdown
    await clients["openai"].close()
    print("OpenAI client closed")


app = FastAPI(
    title="AI Chat API",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# CORS Configuration
# ============================================================================

origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    os.getenv("FRONTEND_URL", ""),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in origins if o],  # Filter empty strings
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Request-ID"],
    max_age=600,
)


# ============================================================================
# Streaming Logic
# ============================================================================

async def stream_openai_response(
    messages: list[dict],
    model: str,
    temperature: float,
    max_tokens: Optional[int],
) -> AsyncGenerator[str, None]:
    """
    Stream OpenAI chat completion token-by-token.

    Yields:
        Token content as strings

    Raises:
        RateLimitError: OpenAI rate limit exceeded
        APIError: OpenAI API error
    """
    response = await clients["openai"].chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content

        # Check for finish reason
        finish_reason = chunk.choices[0].finish_reason
        if finish_reason:
            yield f"\n__FINISH__{finish_reason}"


async def generate_sse_stream(
    request: Request,
    chat_request: ChatRequest,
) -> AsyncGenerator[str, None]:
    """
    Generate SSE-formatted stream with error handling.

    Yields:
        SSE-formatted events
    """
    try:
        # Convert Pydantic models to dicts
        messages = [msg.dict() for msg in chat_request.messages]

        token_count = 0
        finish_reason = None

        # Stream tokens
        async for token in stream_openai_response(
            messages=messages,
            model=chat_request.model,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
        ):
            # Check for client disconnect
            if await request.is_disconnected():
                print(f"Client disconnected after {token_count} tokens")
                break

            # Check for finish marker
            if token.startswith("\n__FINISH__"):
                finish_reason = token.replace("\n__FINISH__", "")
                continue

            token_count += 1

            # Format as SSE
            data = json.dumps({"token": token})
            yield f"data: {data}\n\n"

            # Small delay for backpressure
            await asyncio.sleep(0)

        # Send completion event
        completion_data = json.dumps({
            "tokens": token_count,
            "finish_reason": finish_reason
        })
        yield f"event: done\ndata: {completion_data}\n\n"

    except asyncio.CancelledError:
        print("Stream cancelled by client disconnect")
        # Don't yield anything - connection is closed

    except RateLimitError as e:
        error_msg = e.body.get("message", "OpenAI API rate limit exceeded")
        error_data = json.dumps({"error": error_msg, "type": "rate_limit"})
        yield f"event: error\ndata: {error_data}\n\n"

    except APIError as e:
        error_data = json.dumps({"error": str(e), "type": "api_error"})
        yield f"event: error\ndata: {error_data}\n\n"

    except Exception as e:
        print(f"Unexpected error during streaming: {e}")
        error_data = json.dumps({
            "error": "An unexpected error occurred",
            "type": "internal_error"
        })
        yield f"event: error\ndata: {error_data}\n\n"


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/chat/stream")
async def chat_stream(request: Request, chat_request: ChatRequest):
    """
    Stream OpenAI chat completion responses.

    Returns:
        SSE stream with token events
    """
    if not chat_request.stream:
        raise HTTPException(
            status_code=400,
            detail="This endpoint requires stream=true"
        )

    return StreamingResponse(
        generate_sse_stream(request, chat_request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@app.post("/chat")
async def chat_non_streaming(chat_request: ChatRequest):
    """Non-streaming chat endpoint for comparison."""
    if chat_request.stream:
        raise HTTPException(
            status_code=400,
            detail="This endpoint requires stream=false"
        )

    messages = [msg.dict() for msg in chat_request.messages]

    response = await clients["openai"].chat.completions.create(
        model=chat_request.model,
        messages=messages,
        stream=False,
        temperature=chat_request.temperature,
        max_tokens=chat_request.max_tokens,
    )

    return {
        "content": response.choices[0].message.content,
        "finish_reason": response.choices[0].finish_reason,
        "usage": response.usage.dict()
    }


# ============================================================================
# Development
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### Environment Configuration

```bash
# .env
OPENAI_API_KEY=sk-...
FRONTEND_URL=https://yourdomain.com
```

### Dependencies

```toml
# pyproject.toml
[project]
name = "ai-chat-api"
version = "1.0.0"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "openai>=1.50.0",
    "pydantic>=2.9.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
    "pydantic-to-typescript>=1.0.0",
]
```

---

## 11. Testing Streaming Endpoints

### Test with curl

```bash
# Basic test
curl -N http://localhost:8000/stream

# With POST data
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "model": "gpt-3.5-turbo"
  }'
```

### Test with Python (httpx)

```python
import httpx
import json

async def test_streaming():
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8000/chat/stream",
            json={
                "messages": [{"role": "user", "content": "Hello!"}],
                "model": "gpt-3.5-turbo"
            },
            timeout=30.0
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    print(data["token"], end="", flush=True)
                elif line.startswith("event: done"):
                    print("\n[Stream complete]")
                elif line.startswith("event: error"):
                    # Next line contains error data
                    pass

# Run
import asyncio
asyncio.run(test_streaming())
```

### Test with pytest

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_streaming_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat/stream",
            json={
                "messages": [{"role": "user", "content": "Say 'test'"}],
                "stream": True
            }
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"

        # Collect all tokens
        tokens = []
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                tokens.append(data["token"])

        assert len(tokens) > 0
        assert "".join(tokens) != ""
```

---

## Summary

### Key Takeaways

1. **Use `text/event-stream` media type** to prevent browser buffering
2. **Always check `await request.is_disconnected()`** in long-running streams
3. **Use `async def` with `await asyncio.sleep(0)`** or `def` with `time.sleep()`
4. **Add `X-Accel-Buffering: no` header** for nginx deployments
5. **Wrap generators in error handling** for production reliability
6. **Use explicit CORS origins** when `allow_credentials=True`
7. **Test with multiple clients** (curl, httpx, browser) to verify streaming
8. **Consider `sse-starlette`** for production SSE implementation
9. **Monitor for middleware** (GZip, logging) that may buffer responses
10. **Generate TypeScript types** from Pydantic models for type safety

### Common Patterns Summary

| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| Basic SSE | Simple events | `StreamingResponse` + `text/event-stream` |
| OpenAI Streaming | Token-by-token AI | `AsyncOpenAI` + async generator |
| Error Handling | Production reliability | Wrapper generator with try/except |
| Client Disconnect | Resource cleanup | `request.is_disconnected()` check |
| CORS | Cross-origin requests | `CORSMiddleware` with explicit origins |
| Nginx Proxy | Production deployment | `X-Accel-Buffering: no` header |
| Type Safety | Frontend integration | `pydantic-to-typescript` |

### Performance Considerations

- **Use `AsyncOpenAI`** for non-blocking I/O
- **Add `await asyncio.sleep(0)`** for backpressure
- **Set reasonable timeouts** on long-lived connections
- **Monitor connection counts** (keep-alive pools)
- **Consider WebSockets** for bidirectional communication
- **Use connection pooling** for database queries in generators

### Security Considerations

- **Validate all inputs** with Pydantic models
- **Never expose API keys** in responses or logs
- **Use explicit CORS origins** (no wildcards in production)
- **Implement rate limiting** on streaming endpoints
- **Add authentication** (JWT, API keys) to protect endpoints
- **Set max token limits** to prevent abuse
- **Log and monitor** streaming errors and disconnects

---

## Additional Resources

### Official Documentation
- FastAPI: https://fastapi.tiangolo.com/
- Starlette: https://www.starlette.io/
- OpenAI Python SDK: https://github.com/openai/openai-python
- Server-Sent Events Spec: https://html.spec.whatwg.org/multipage/server-sent-events.html

### Community Resources
- FastAPI GitHub Discussions: https://github.com/fastapi/fastapi/discussions
- Stack Overflow [fastapi]: https://stackoverflow.com/questions/tagged/fastapi
- Awesome FastAPI: https://github.com/mjhea0/awesome-fastapi

### Tools
- sse-starlette: https://github.com/sysid/sse-starlette
- pydantic-to-typescript: https://github.com/phillipdupuis/pydantic-to-typescript
- httpx: https://www.python-httpx.org/
- uvicorn: https://www.uvicorn.org/
