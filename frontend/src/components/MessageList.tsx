/**
 * Scrollable message list container with auto-scroll.
 */
import { useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
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
      {messages.length === 0 && !streamingMessage ? (
        <div className="h-full flex items-center justify-center text-center">
          <div>
            <p className="text-gray-500 text-lg mb-2">No messages yet</p>
            <p className="text-gray-400 text-sm">Start a conversation by typing a message below</p>
          </div>
        </div>
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
