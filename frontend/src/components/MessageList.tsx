/**
 * Scrollable message list container with auto-scroll.
 */
import { useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';
import { EmptyState } from './EmptyState';
import { MessageSquare } from 'lucide-react';
import type { Message, Source } from '@/types';

interface MessageListProps {
  messages: Message[];
  streamingMessage?: { content: string; sources?: Source[] };
  isStreaming?: boolean;
  onFeedback?: (messageId: string, rating: number) => void;
}

export function MessageList({
  messages,
  streamingMessage,
  isStreaming = false,
  onFeedback,
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar px-4 py-6 space-y-4">
      {messages.length === 0 && !streamingMessage && !isStreaming ? (
        <EmptyState
          icon={MessageSquare}
          title="No messages yet"
          description="Start a conversation by typing a message below or try one of these examples"
          suggestions={[
            "How do I reset my password?",
            "What are the current promotions?",
            "Explain the billing process",
          ]}
          onSuggestionClick={(suggestion) => {
            // This will be handled by parent component
            console.log('Suggestion clicked:', suggestion);
          }}
        />
      ) : (
        <>
          {/* Existing messages */}
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onFeedback={
                message.role === 'assistant' && onFeedback
                  ? (rating) => onFeedback(message.id, rating)
                  : undefined
              }
            />
          ))}

          {/* Typing indicator (before streaming starts) */}
          {isStreaming && !streamingMessage && <TypingIndicator />}

          {/* Streaming message */}
          {streamingMessage && (
            <ChatMessage
              message={{ role: 'assistant', content: streamingMessage.content, sources: streamingMessage.sources }}
              isStreaming={isStreaming}
            />
          )}

          {/* Auto-scroll anchor */}
          <div ref={bottomRef} />
        </>
      )}
    </div>
  );
}
