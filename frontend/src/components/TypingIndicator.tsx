/**
 * Typing indicator component - shows AI is "thinking" before streaming starts.
 */
import { Bot } from 'lucide-react';

export function TypingIndicator() {
  return (
    <div className="flex gap-3 p-4 rounded-lg bg-white border border-gray-200">
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-600 text-white">
        <Bot className="w-5 h-5" />
      </div>

      {/* Typing animation */}
      <div className="flex items-center space-x-1 pt-2">
        <div
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
          style={{ animationDelay: '0ms', animationDuration: '1.4s' }}
        />
        <div
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
          style={{ animationDelay: '200ms', animationDuration: '1.4s' }}
        />
        <div
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
          style={{ animationDelay: '400ms', animationDuration: '1.4s' }}
        />
      </div>
    </div>
  );
}
