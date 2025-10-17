/**
 * TypeScript types matching the backend API schemas.
 */

export interface User {
  id: string;
  attid: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  roles: string[];
}

export interface LoginRequest {
  attid: string;
  password: string;
}

export interface SignupRequest {
  attid: string;
  email: string;
  password: string;
  full_name: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  sources?: Source[];
  created_at: string;
}

export interface Source {
  title: string;
  url: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  service_type: 'askatt' | 'askdocs';
  configuration_id?: string;
  title?: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ConversationListItem {
  id: string;
  service_type: 'askatt' | 'askdocs';
  title?: string;
  configuration_id?: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  configuration_id?: string;
}

export interface Configuration {
  id: string;
  domain_id: string;
  config_key: string;
  display_name: string;
  description?: string;
  environment: 'stage' | 'production';
  is_active: boolean;
  domain: Domain;
}

export interface Domain {
  id: string;
  domain_key: string;
  display_name: string;
  description?: string;
}

export interface FeedbackRequest {
  rating: number;
  comment?: string;
}

export interface Feedback {
  id: string;
  message_id: string;
  rating: number;
  comment?: string;
  created_at: string;
}

// SSE Event types
export interface SSETokenEvent {
  type: 'token';
  content: string;
}

export interface SSESourcesEvent {
  type: 'sources';
  sources: Source[];
}

export interface SSEUsageEvent {
  type: 'usage';
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface SSEConversationIdEvent {
  type: 'conversation_id';
  conversation_id: string;
}

export interface SSEEndEvent {
  type: 'end';
}

export interface SSEErrorEvent {
  type: 'error';
  content: string;
}

export type SSEEvent =
  | SSETokenEvent
  | SSESourcesEvent
  | SSEUsageEvent
  | SSEConversationIdEvent
  | SSEEndEvent
  | SSEErrorEvent;

// Admin types
export interface Role {
  id: string;
  name: string;
  description?: string;
  created_at: string;
}

export interface UserRoleAssignment {
  user_id: string;
  role_ids: string[];
}
