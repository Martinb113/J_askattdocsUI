/**
 * Hook for Server-Sent Events (SSE) streaming chat.
 * Handles token-by-token streaming from the backend.
 */
import { useState, useCallback, useRef } from 'react';
import type { ChatRequest, SSEEvent, Source } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface StreamingState {
  isStreaming: boolean;
  message: string;
  sources: Source[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  } | null;
  conversationId: string | null;
  error: string | null;
}

export function useStreamingChat(serviceType: 'askatt' | 'askdocs') {
  const [state, setState] = useState<StreamingState>({
    isStreaming: false,
    message: '',
    sources: [],
    usage: null,
    conversationId: null,
    error: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (request: ChatRequest) => {
      // Reset state
      setState({
        isStreaming: true,
        message: '',
        sources: [],
        usage: null,
        conversationId: request.conversation_id || null,
        error: null,
      });

      // Create abort controller for cancellation
      abortControllerRef.current = new AbortController();

      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          throw new Error('Not authenticated');
        }

        const endpoint =
          serviceType === 'askatt'
            ? `${API_BASE_URL}/api/v1/chat/askatt`
            : `${API_BASE_URL}/api/v1/chat/askdocs`;

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(request),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Request failed');
        }

        if (!response.body) {
          throw new Error('Response body is null');
        }

        // Read SSE stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let accumulatedMessage = '';
        let accumulatedSources: Source[] = [];
        let accumulatedUsage = null;
        let newConversationId = request.conversation_id || null;

        // Buffer for incomplete SSE events across chunks
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          // Decode chunk and append to buffer
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          // Parse SSE events (format: "data: {...}\n\n")
          // Split by double newline to get complete SSE events
          const events = buffer.split('\n\n');

          // Keep the last potentially incomplete event in the buffer
          buffer = events.pop() || '';

          for (const eventBlock of events) {
            // Each event block should contain one or more "data: " lines
            const lines = eventBlock.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const jsonStr = line.slice(6).trim(); // Remove "data: " prefix and trim whitespace

                // Skip empty data lines
                if (!jsonStr) {
                  continue;
                }

                try {
                  const event: SSEEvent = JSON.parse(jsonStr);

                  switch (event.type) {
                    case 'token':
                      accumulatedMessage += event.content;
                      setState((prev) => ({
                        ...prev,
                        message: accumulatedMessage,
                      }));
                      break;

                    case 'sources':
                      accumulatedSources = event.sources;
                      setState((prev) => ({
                        ...prev,
                        sources: accumulatedSources,
                      }));
                      break;

                    case 'usage':
                      accumulatedUsage = event.usage;
                      setState((prev) => ({
                        ...prev,
                        usage: accumulatedUsage,
                      }));
                      break;

                    case 'conversation_id':
                      newConversationId = event.conversation_id;
                      setState((prev) => ({
                        ...prev,
                        conversationId: newConversationId,
                      }));
                      break;

                    case 'end':
                      // Stream complete
                      setState((prev) => ({
                        ...prev,
                        isStreaming: false,
                      }));
                      break;

                    case 'error':
                      throw new Error(event.content);
                  }
                } catch (parseError) {
                  console.error('Failed to parse SSE event:', parseError, 'Line:', jsonStr);
                }
              }
            }
          }
        }

        // Ensure streaming is marked as complete
        setState((prev) => ({
          ...prev,
          isStreaming: false,
        }));

        return {
          message: accumulatedMessage,
          sources: accumulatedSources,
          usage: accumulatedUsage,
          conversationId: newConversationId,
        };
      } catch (error: any) {
        if (error.name === 'AbortError') {
          // User cancelled
          setState((prev) => ({
            ...prev,
            isStreaming: false,
            error: 'Request cancelled',
          }));
        } else {
          setState((prev) => ({
            ...prev,
            isStreaming: false,
            error: error.message || 'Failed to send message',
          }));
        }
        throw error;
      }
    },
    [serviceType]
  );

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      isStreaming: false,
      message: '',
      sources: [],
      usage: null,
      conversationId: null,
      error: null,
    });
  }, []);

  return {
    ...state,
    sendMessage,
    cancelStream,
    reset,
  };
}
