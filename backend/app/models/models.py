import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, ForeignKey, Enum, Boolean
)
from sqlalchemy.orm import relationship
from app.core.database import Base, IS_POSTGRES

# If PostgreSQL, try importing pgvector Vector type, otherwise store vector as JSON/TEXT
PG_VECTOR_AVAILABLE = False
if IS_POSTGRES:
    try:
        from pgvector.sqlalchemy import Vector
        PG_VECTOR_AVAILABLE = True
    except ImportError:
        PG_VECTOR_AVAILABLE = False

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="officer")  # "admin" or "officer"
    department = Column(String(100), default="Assam Administrative Staff College")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="uploader", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    category = Column(String(100), default="General Order") # Rules, Manuals, Circulars, Office Orders, Notifications
    file_size = Column(Integer, default=0) # in bytes
    page_count = Column(Integer, default=0)
    processing_status = Column(String(50), default="PENDING") # PENDING, PROCESSING, INDEXED, FAILED
    error_message = Column(Text, nullable=True)
    source_classification = Column(String(100), default="Public Official Document")
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    uploader = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    page_number = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    
    # Store embedding as pgvector Vector or JSON text
    if PG_VECTOR_AVAILABLE:
        embedding = Column(Vector(384), nullable=True)
    else:
        embedding = Column(Text, nullable=True) # Serialized JSON array of floats

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="chunks")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), default="New Query")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(String(20), nullable=False) # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    citations = Column(Text, nullable=True) # JSON serialized list of source citations
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False) # LOGIN, UPLOAD, DELETE, QUERY, GENERATE_DRAFT, SUMMARIZE
    metadata_json = Column(Text, nullable=True) # JSON metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
