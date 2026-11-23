import { 
  User, DocumentItem, ChatResponse, ConversationItem, ConversationDetail, 
  DraftingRequest, DraftingResponse, AuditLogItem, DashboardStats 
} from '../types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

function getAuthHeaders(): HeadersInit {
  const token = typeof window !== 'undefined' ? localStorage.getItem('govsaarthi_token') : null;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  // Auth
  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json();
    if (typeof window !== 'undefined') {
      localStorage.setItem('govsaarthi_token', data.access_token);
      localStorage.setItem('govsaarthi_user', JSON.stringify(data.user));
    }
    return data;
  },

  async getMe(): Promise<User | null> {
    const token = typeof window !== 'undefined' ? localStorage.getItem('govsaarthi_token') : null;
    if (!token) return null;
    try {
      const res = await fetch(`${BASE_URL}/api/auth/me`, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('govsaarthi_token');
      localStorage.removeItem('govsaarthi_user');
    }
  },

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${BASE_URL}/api/dashboard/stats`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load dashboard statistics');
    return res.json();
  },

  // Documents
  async getDocuments(category?: string, search?: string): Promise<DocumentItem[]> {
    const params = new URLSearchParams();
    if (category && category !== 'All') params.set('category', category);
    if (search) params.set('search', search);

    const res = await fetch(`${BASE_URL}/api/documents?${params.toString()}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async uploadDocument(file: File, category: string, classification: string): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    formData.append('source_classification', classification);

    const token = typeof window !== 'undefined' ? localStorage.getItem('govsaarthi_token') : null;
    const headers: HeadersInit = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${BASE_URL}/api/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async deleteDocument(id: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/api/documents/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  getDocumentFileUrl(id: string, pageNumber?: number): string {
    const baseUrl = `${BASE_URL}/api/documents/${id}/file`;
    return pageNumber ? `${baseUrl}#page=${pageNumber}` : baseUrl;
  },

  // Chat & RAG
  async askQuestion(question: string, conversationId?: string, documentId?: string): Promise<ChatResponse> {
    const res = await fetch(`${BASE_URL}/api/chat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        question,
        conversation_id: conversationId,
        document_id: documentId,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to process question' }));
      throw new Error(err.detail || 'Failed to process question');
    }
    return res.json();
  },

  async getConversations(): Promise<ConversationItem[]> {
    const res = await fetch(`${BASE_URL}/api/conversations`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
  },

  async getConversationDetail(id: string): Promise<ConversationDetail> {
    const res = await fetch(`${BASE_URL}/api/conversations/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch conversation history');
    return res.json();
  },

  // Drafting Studio
  async generateDraft(request: DraftingRequest): Promise<DraftingResponse> {
    const res = await fetch(`${BASE_URL}/api/drafting/generate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(request),
    });
    if (!res.ok) throw new Error('Draft generation failed');
    return res.json();
  },

  async summarizeDocument(documentId: string): Promise<DraftingResponse> {
    const res = await fetch(`${BASE_URL}/api/drafting/summarize`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ document_id: documentId }),
    });
    if (!res.ok) throw new Error('Summarization failed');
    return res.json();
  },

  // Audit Logs
  async getAuditLogs(limit: number = 50): Promise<AuditLogItem[]> {
    const res = await fetch(`${BASE_URL}/api/audit-logs?limit=${limit}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },
};
