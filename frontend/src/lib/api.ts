/**
 * API client for backend communication.
 */
import axios, { AxiosError, AxiosInstance } from 'axios';
import type {
  LoginRequest,
  LoginResponse,
  SignupRequest,
  User,
  Conversation,
  ConversationListItem,
  Configuration,
  FeedbackRequest,
  Feedback,
  Role,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to attach token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>('/api/v1/auth/login', data);
    return response.data;
  }

  async signup(data: SignupRequest): Promise<User> {
    const response = await this.client.post<User>('/api/v1/auth/signup', data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/api/v1/auth/me');
    return response.data;
  }

  // Conversations
  async getConversations(serviceType?: 'askatt' | 'askdocs'): Promise<ConversationListItem[]> {
    const params = serviceType ? { service_type: serviceType } : {};
    const response = await this.client.get<ConversationListItem[]>('/api/v1/chat/conversations', {
      params,
    });
    return response.data;
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    const response = await this.client.get<Conversation>(
      `/api/v1/chat/conversations/${conversationId}`
    );
    return response.data;
  }

  async deleteConversation(conversationId: string): Promise<void> {
    await this.client.delete(`/api/v1/chat/conversations/${conversationId}`);
  }

  // Configurations
  async getConfigurations(environment?: 'stage' | 'production'): Promise<Configuration[]> {
    const params = environment ? { environment } : {};
    const response = await this.client.get<Configuration[]>('/api/v1/chat/configurations', {
      params,
    });
    return response.data;
  }

  // Feedback
  async submitFeedback(messageId: string, data: FeedbackRequest): Promise<Feedback> {
    const response = await this.client.post<Feedback>(
      `/api/v1/chat/messages/${messageId}/feedback`,
      data
    );
    return response.data;
  }

  // Admin
  async getAllUsers(): Promise<User[]> {
    const response = await this.client.get<User[]>('/api/v1/admin/users');
    return response.data;
  }

  async getRoles(): Promise<Role[]> {
    const response = await this.client.get<Role[]>('/api/v1/admin/roles');
    return response.data;
  }

  async assignUserRoles(userId: string, roleIds: string[]): Promise<User> {
    const response = await this.client.post<User>(`/api/v1/admin/users/${userId}/roles`, {
      user_id: userId,
      role_ids: roleIds,
    });
    return response.data;
  }

  async getAllConfigurations(): Promise<Configuration[]> {
    const response = await this.client.get<Configuration[]>('/api/v1/admin/configurations');
    return response.data;
  }

  // Helper to get auth headers
  getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}

export const apiClient = new ApiClient();
export default apiClient;
