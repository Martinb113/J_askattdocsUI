/**
 * Conversation list sidebar component - displays past conversations grouped by date.
 */
import { useEffect, useState } from 'react';
import { MessageSquare, Trash2, Search, Plus } from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '@/lib/api';
import type { ConversationListItem } from '@/types';
import { formatRelativeTime } from '@/lib/utils';
import { Button } from './ui/Button';

interface ConversationListProps {
  onSelectConversation: (conversationId: string) => void;
  currentConversationId: string | null;
  onNewChat: () => void;
}

export function ConversationList({
  onSelectConversation,
  currentConversationId,
  onNewChat,
}: ConversationListProps) {
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Failed to load conversations:', error);
      toast.error('Failed to load conversations');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this conversation?')) {
      try {
        await apiClient.deleteConversation(id);
        toast.success('Conversation deleted');
        await loadConversations();
        // If deleted conversation was active, trigger new chat
        if (id === currentConversationId) {
          onNewChat();
        }
      } catch (error) {
        toast.error('Failed to delete conversation');
      }
    }
  };

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const groupedConversations = groupByDate(filteredConversations);

  return (
    <div className="h-full flex flex-col bg-gray-50 border-r border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <Button onClick={onNewChat} className="w-full mb-3">
          <Plus className="w-4 h-4 mr-2" />
          New Chat
        </Button>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500 text-sm">Loading...</div>
        ) : filteredConversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            {searchQuery ? 'No matching conversations' : 'No conversations yet'}
          </div>
        ) : (
          Object.entries(groupedConversations).map(([group, convs]) => (
            <div key={group}>
              <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider bg-gray-100 sticky top-0">
                {group}
              </div>
              {convs.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => onSelectConversation(conv.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-100 transition-colors border-b border-gray-200 cursor-pointer ${
                    currentConversationId === conv.id
                      ? 'bg-primary-50 border-l-4 border-l-primary-600'
                      : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <MessageSquare className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        <span
                          className={`text-xs px-2 py-0.5 rounded ${
                            conv.service_type === 'askatt'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-purple-100 text-purple-700'
                          }`}
                        >
                          {conv.service_type === 'askatt' ? 'AskAT&T' : 'AskDocs'}
                        </span>
                      </div>
                      <p className="text-sm font-medium text-gray-900 truncate mb-1">
                        {conv.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatRelativeTime(conv.created_at)}
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleDelete(conv.id, e)}
                      className="ml-2 p-1 text-gray-400 hover:text-red-600 transition-colors flex-shrink-0"
                      title="Delete conversation"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// Helper to group conversations by date
function groupByDate(conversations: ConversationListItem[]) {
  const now = new Date();
  const groups: Record<string, ConversationListItem[]> = {
    Today: [],
    Yesterday: [],
    'Last 7 days': [],
    Older: [],
  };

  conversations.forEach((conv) => {
    const date = new Date(conv.created_at);
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) groups['Today'].push(conv);
    else if (diffDays === 1) groups['Yesterday'].push(conv);
    else if (diffDays <= 7) groups['Last 7 days'].push(conv);
    else groups['Older'].push(conv);
  });

  // Remove empty groups
  Object.keys(groups).forEach((key) => {
    if (groups[key].length === 0) delete groups[key];
  });

  return groups;
}
