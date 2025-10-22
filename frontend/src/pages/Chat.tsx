/**
 * Main chat page with service selector and streaming chat.
 */
import { useState, useEffect, FormEvent } from 'react';
import { toast } from 'sonner';
import { useStreamingChat } from '@/hooks/useStreamingChat';
import { MessageList } from '@/components/MessageList';
import { ConversationList } from '@/components/ConversationList';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';
import { Send, StopCircle, Menu } from 'lucide-react';
import apiClient from '@/lib/api';
import type { Message, Configuration } from '@/types';

type ServiceType = 'askatt' | 'askdocs';

export function Chat() {
  const [serviceType, setServiceType] = useState<ServiceType>('askatt');
  const [selectedConfig, setSelectedConfig] = useState<string>('');
  const [configurations, setConfigurations] = useState<Configuration[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const {
    sendMessage,
    message: streamingMessage,
    sources: streamingSources,
    isStreaming,
    conversationId: newConversationId,
    error,
    cancelStream,
    reset,
  } = useStreamingChat(serviceType);

  // Restore conversation state from localStorage on mount
  useEffect(() => {
    const savedConversationId = localStorage.getItem('current_conversation_id');
    if (savedConversationId) {
      loadConversation(savedConversationId);
    }
  }, []);

  // Save current conversation ID to localStorage
  useEffect(() => {
    if (conversationId) {
      localStorage.setItem('current_conversation_id', conversationId);
    } else {
      localStorage.removeItem('current_conversation_id');
    }
  }, [conversationId]);

  // Load configurations for AskDocs
  useEffect(() => {
    if (serviceType === 'askdocs') {
      loadConfigurations();
    }
  }, [serviceType]);

  // Update conversation ID when new one is created
  useEffect(() => {
    if (newConversationId) {
      setConversationId(newConversationId);
    }
  }, [newConversationId]);

  const loadConfigurations = async () => {
    try {
      const configs = await apiClient.getConfigurations();
      setConfigurations(configs);
      // Auto-select first config if available
      if (configs.length > 0 && !selectedConfig) {
        setSelectedConfig(configs[0].id);
      }
    } catch (error) {
      console.error('Failed to load configurations:', error);
      toast.error('Failed to load configurations');
    }
  };

  const handleSubmit = async (e: FormEvent, messageToSend?: string) => {
    e.preventDefault();

    const messageContent = messageToSend || inputMessage;

    if (!messageContent.trim() || isStreaming) {
      return;
    }

    // Validate configuration for AskDocs
    if (serviceType === 'askdocs' && !selectedConfig) {
      toast.error('Please select a configuration for AskDocs');
      return;
    }

    // Add user message to display
    const userMessage: Message = {
      id: Date.now().toString(),
      conversation_id: conversationId || '',
      role: 'user',
      content: messageContent,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!messageToSend) {
      setInputMessage('');
    }

    try {
      // Send message with streaming
      const result = await sendMessage({
        message: messageContent,
        conversation_id: conversationId || undefined,
        configuration_id: serviceType === 'askdocs' ? selectedConfig : undefined,
      });

      // Add assistant message to display
      if (result) {
        const assistantMessage: Message = {
          id: result.messageId || Date.now().toString(), // Use real messageId from backend
          conversation_id: result.conversationId || conversationId || '',
          role: 'assistant',
          content: result.message,
          sources: result.sources,
          token_usage: result.usage || undefined,
          created_at: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
        reset();
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleFeedback = async (messageId: string, rating: number, comment?: string) => {
    try {
      await apiClient.submitFeedback(messageId, { rating, comment });
      toast.success(rating >= 4 ? 'Thanks for the positive feedback!' : 'Thank you for your feedback');
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      toast.error('Failed to submit feedback');
    }
  };

  const handleRegenerate = async (messageId: string) => {
    // Find the assistant message to regenerate
    const messageIndex = messages.findIndex((msg) => msg.id === messageId);
    if (messageIndex === -1 || messages[messageIndex].role !== 'assistant') {
      toast.error('Cannot regenerate this message');
      return;
    }

    // Find the user message that preceded this assistant message
    let userMessageContent = '';
    for (let i = messageIndex - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        userMessageContent = messages[i].content;
        break;
      }
    }

    if (!userMessageContent) {
      toast.error('Cannot find the original question');
      return;
    }

    // Remove the assistant message from the list
    setMessages((prev) => prev.filter((msg) => msg.id !== messageId));

    // Resend the user message
    try {
      await handleSubmit(new Event('submit') as any, userMessageContent);
      toast.info('Regenerating response...');
    } catch (error) {
      console.error('Failed to regenerate message:', error);
      toast.error('Failed to regenerate response');
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    localStorage.removeItem('current_conversation_id');
    reset();
    toast.info('Started new conversation');
  };

  const loadConversation = async (conversationId: string) => {
    try {
      const conv = await apiClient.getConversation(conversationId);
      setMessages(conv.messages);
      setConversationId(conv.id);
      setServiceType(conv.service_type as ServiceType);
      if (conv.configuration_id) {
        setSelectedConfig(conv.configuration_id);
      }
      toast.success('Conversation loaded');
    } catch (error) {
      console.error('Failed to load conversation:', error);
      toast.error('Failed to load conversation');
    }
  };

  const handleServiceChange = (service: ServiceType) => {
    setServiceType(service);
    setMessages([]);
    setConversationId(null);
    setSelectedConfig('');
    reset();
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-80' : 'w-0'
        } transition-all duration-300 overflow-hidden flex-shrink-0`}
      >
        <ConversationList
          onSelectConversation={loadConversation}
          currentConversationId={conversationId}
          onNewChat={handleNewChat}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="border-b border-gray-200 p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              {/* Mobile sidebar toggle */}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title={sidebarOpen ? 'Hide sidebar' : 'Show sidebar'}
              >
                <Menu className="w-5 h-5 text-gray-600" />
              </button>
              <h1 className="text-2xl font-bold text-gray-900">AI Chat</h1>
            </div>
            <Button variant="outline" size="sm" onClick={handleNewChat}>
              New Chat
            </Button>
          </div>

        {/* Service Selector */}
        <div className="flex items-center space-x-4">
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => handleServiceChange('askatt')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                serviceType === 'askatt'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              AskAT&T
            </button>
            <button
              onClick={() => handleServiceChange('askdocs')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                serviceType === 'askdocs'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              AskDocs
            </button>
          </div>

          {/* Configuration Selector (for AskDocs) */}
          {serviceType === 'askdocs' && (
            <select
              value={selectedConfig}
              onChange={(e) => setSelectedConfig(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
            >
              <option value="">Select Configuration...</option>
              {configurations.map((config) => (
                <option key={config.id} value={config.id}>
                  {config.display_name} ({config.environment})
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Service Description */}
        <p className="mt-3 text-sm text-gray-600">
          {serviceType === 'askatt'
            ? 'General AI assistant powered by OpenAI (MOCK mode for local development)'
            : 'Domain-specific knowledge base chat with source attribution (MOCK mode for local development)'}
        </p>
        </div>

        {/* Messages */}
      <MessageList
        messages={messages}
        streamingMessage={
          streamingMessage ? { content: streamingMessage, sources: streamingSources } : undefined
        }
        isStreaming={isStreaming}
        onFeedback={handleFeedback}
        onRegenerate={handleRegenerate}
      />

        {/* Error Display */}
        {error && (
          <div className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 text-red-800 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex items-end space-x-2">
          <div className="flex-1">
            <Textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={
                serviceType === 'askatt'
                  ? 'Ask me anything...'
                  : 'Search the knowledge base...'
              }
              rows={1}
              autoResize
              className="resize-none max-h-32"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e as any);
                }
              }}
            />
          </div>

          {isStreaming ? (
            <Button type="button" variant="danger" onClick={cancelStream}>
              <StopCircle className="w-4 h-4 mr-2" />
              Stop
            </Button>
          ) : (
            <Button type="submit" disabled={!inputMessage.trim()}>
              <Send className="w-4 h-4 mr-2" />
              Send
            </Button>
          )}
        </form>

          <p className="mt-2 text-xs text-gray-500">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
