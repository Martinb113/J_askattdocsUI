/**
 * Chat message component with markdown rendering and source attribution.
 */
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Bot, ExternalLink, ThumbsUp, ThumbsDown, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';
import type { Message, Source } from '@/types';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  message: Message | { role: 'user' | 'assistant'; content: string; sources?: Source[] };
  isStreaming?: boolean;
  onFeedback?: (rating: number) => void;
}

export function ChatMessage({ message, isStreaming = false, onFeedback }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      toast.success('Copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error('Failed to copy');
    }
  };

  return (
    <div
      className={cn(
        'group relative flex gap-3 p-4 rounded-lg',
        isUser ? 'bg-primary-50' : 'bg-white border border-gray-200'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-primary-600 text-white' : 'bg-gray-600 text-white'
        )}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Copy Button (appears on hover for assistant messages) */}
      {!isUser && !isStreaming && (
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-gray-600 bg-white rounded opacity-0 group-hover:opacity-100 transition-opacity shadow-sm border border-gray-200"
          title="Copy message"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-600" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      )}

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Role Label */}
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-medium text-gray-900">
            {isUser ? 'You' : 'AI Assistant'}
          </p>
          {isStreaming && (
            <span className="text-xs text-gray-500 flex items-center">
              <span className="animate-pulse mr-1">●</span>
              Generating...
            </span>
          )}
        </div>

        {/* Message Content with Markdown */}
        <div className="prose prose-sm max-w-none markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>

        {/* Sources (for AskDocs) */}
        {'sources' in message && message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm font-medium text-gray-700 mb-2">Sources:</p>
            <div className="space-y-2">
              {message.sources.map((source, index) => (
                <a
                  key={index}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-sm text-primary-600 hover:text-primary-700 hover:underline"
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  {source.title}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Feedback Buttons (only for assistant messages) */}
        {!isUser && onFeedback && !isStreaming && (
          <div className="mt-3 flex items-center space-x-2">
            <p className="text-xs text-gray-500">Was this helpful?</p>
            <button
              onClick={() => onFeedback(5)}
              className="p-1 text-gray-400 hover:text-green-600 transition-colors"
              title="Helpful"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => onFeedback(1)}
              className="p-1 text-gray-400 hover:text-red-600 transition-colors"
              title="Not helpful"
            >
              <ThumbsDown className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Token Usage (if available) */}
        {'token_usage' in message && message.token_usage && (
          <div className="mt-2 text-xs text-gray-400">
            Tokens: {message.token_usage.total_tokens} (prompt: {message.token_usage.prompt_tokens}
            , completion: {message.token_usage.completion_tokens})
          </div>
        )}
      </div>
    </div>
  );
}
