from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserLogin(BaseModel):
    email: str = Field(..., min_length=3)
    password: str

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    role: Optional[str] = "officer"
    department: Optional[str] = "Assam Administrative Staff College"

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    department: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Document Schemas ---
class DocumentResponse(BaseModel):
    id: str
    filename: str
    category: str
    file_size: int
    page_count: int
    processing_status: str
    error_message: Optional[str] = None
    source_classification: str
    created_at: datetime
    uploaded_by: Optional[str] = None

    class Config:
        from_attributes = True

class DocumentDetail(DocumentResponse):
    chunk_count: int = 0


# --- Citation Schemas ---
class CitationItem(BaseModel):
    citation_id: str
    document_id: str
    document_name: str
    page_number: int
    excerpt: str
    similarity_score: float = 0.0
    rule_reference: Optional[str] = None
    total_pages: Optional[int] = None


# --- Chat & RAG Schemas ---
class ChatMessage(BaseModel):
    id: str
    role: str
    content: str
    citations: Optional[List[CitationItem]] = None
    created_at: datetime

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    question: str
    document_id: Optional[str] = None # Optional filter to search a specific document

class ChatResponse(BaseModel):
    conversation_id: str
    question: str
    answer: str
    citations: List[CitationItem]
    grounded: bool
    created_at: datetime

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    message_count: int = 0

class ConversationDetail(BaseModel):
    id: str
    title: str
    created_at: datetime
    messages: List[ChatMessage]


# --- Drafting Schemas ---
class DraftingRequest(BaseModel):
    draft_type: str = Field(..., description="office_note, formal_letter, office_order, summary")
    subject: str = Field(..., min_length=3)
    instructions: str = Field(..., min_length=5)
    document_ids: Optional[List[str]] = None
    target_authority: Optional[str] = "Commissioner & Secretary, Government of Assam"
    reference_number: Optional[str] = None

class DraftingResponse(BaseModel):
    draft_type: str
    subject: str
    draft_content: str
    references_used: List[CitationItem]
    disclaimer: str = "DRAFT ONLY - Requires human review, verification and authorized signature before issuance."
    created_at: datetime

class SummarizeRequest(BaseModel):
    document_id: str
    summary_type: str = "standard" # executive, comprehensive, bullet_points


# --- Audit Schemas ---
class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Dashboard Stats ---
class DashboardStats(BaseModel):
    total_documents: int
    indexed_documents: int
    total_queries: int
    total_drafts: int
    recent_questions: List[Dict[str, Any]]
