export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'officer';
  department?: string;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  category: string;
  file_size: number;
  page_count: number;
  processing_status: 'PENDING' | 'PROCESSING' | 'INDEXED' | 'FAILED';
  error_message?: string;
  source_classification: string;
  created_at: string;
  uploaded_by?: string;
  chunk_count?: number;
}

export interface CitationItem {
  citation_id: string;
  document_id: string;
  document_name: string;
  page_number: number;
  excerpt: string;
  similarity_score: number;
  rule_reference?: string;
  total_pages?: number;
  highlight_text?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: CitationItem[];
  created_at: string;
}

export interface ConversationItem {
  id: string;
  title: string;
  created_at: string;
  message_count: number;
}

export interface ConversationDetail {
  id: string;
  title: string;
  created_at: string;
  messages: ChatMessage[];
}

export interface ChatResponse {
  conversation_id: string;
  question: string;
  answer: string;
  citations: CitationItem[];
  grounded: boolean;
  created_at: string;
}

export interface DraftingRequest {
  draft_type: 'office_note' | 'formal_letter' | 'office_order' | 'summary';
  subject: string;
  instructions: string;
  document_ids?: string[];
  target_authority?: string;
  reference_number?: string;
}

export interface DraftingResponse {
  draft_type: string;
  subject: string;
  draft_content: string;
  references_used: CitationItem[];
  disclaimer: string;
  created_at: string;
}

export interface AuditLogItem {
  id: string;
  user_id?: string;
  user_email?: string;
  action: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface DashboardStats {
  total_documents: number;
  indexed_documents: number;
  total_queries: number;
  total_drafts: number;
  recent_questions: Array<{
    id: string;
    question: string;
    created_at: string;
  }>;
}
