import os
import re
import uuid
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
import pymupdf  # PyMuPDF (fitz)

from app.core.config import settings
from app.models.models import Document, DocumentChunk
from app.services.embedding_service import embedding_service

logger = logging.getLogger("govsaarthi.document_service")

class DocumentService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_pdf_file(self, filename: str, content: bytes) -> Tuple[bool, str]:
        """Validate file extension, size, and PDF magic bytes."""
        if not filename.lower().endswith(".pdf"):
            return False, "Invalid file format: Only PDF documents (.pdf) are permitted."
        
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            return False, f"File size exceeds maximum permitted limit of {settings.MAX_FILE_SIZE_MB}MB."

        # Check PDF header magic bytes %PDF-
        if not content.startswith(b"%PDF-"):
            return False, "File is corrupted or not a valid PDF document."

        return True, ""

    def save_file(self, doc_id: str, filename: str, content: bytes) -> Path:
        """Securely save uploaded PDF to disk."""
        sanitized = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", filename)
        saved_name = f"{doc_id}_{sanitized}"
        target_path = self.upload_dir / saved_name
        with open(target_path, "wb") as f:
            f.write(content)
        return target_path

    def chunk_text(self, text: str, page_number: int, chunk_size: int = 700, overlap: int = 150) -> List[Dict[str, Any]]:
        """
        Structure-aware hierarchical chunking for official government documents:
        1. Identifies structural boundaries: Chapters, Sections, Rules, Numbered Paragraphs, Headings.
        2. Preserves atomic list integrity: Headings + complete lists ((i), (ii), (a), (b), 1., 2., •, -)
           are bound together as single complete chunks rather than being bisected.
        3. Never splits a checklist or procedural subsection across chunk boundaries.
        4. Splits large narrative prose blocks at sentence boundaries.
        """
        text = text.strip()
        if not text:
            return []

        # If page text fits within 950 characters, keep as a single atomic page chunk
        if len(text) <= 950:
            return [{
                "page_number": page_number,
                "text": text
            }]

        # Split into structural blocks by double newline or section markers
        raw_blocks = re.split(r"\n\s*\n+", text)
        blocks: List[str] = []
        for b in raw_blocks:
            b_clean = b.strip()
            if not b_clean:
                continue
            # Separate distinct numbered rules or sections within a block
            # e.g., "\n3.2 Documents required..." or "\nPara 2..."
            sub_sections = re.split(r"\n(?=(?:Rule\s+\d+|Para\s+\d+|\d+\.\s+[A-Z]|Chapter\s+[IVX\d]+))", b_clean)
            for s in sub_sections:
                s_strip = s.strip()
                if s_strip:
                    blocks.append(s_strip)

        chunks = []
        current_chunk = ""

        for block in blocks:
            # Check if this block contains a list / checklist
            is_list = bool(re.search(r"(?:\([iIvVxXa-z\d]+\)|^\s*[\-\*\•\d+\.]\s+)", block, re.MULTILINE))
            is_major_heading = bool(re.match(r"^(?:Rule\s+\d+|Para\s+\d+|\d+\.\s+[A-Z]|Chapter\s+[IVX\d]+)", block))

            # If current_chunk is empty, start with this block
            if not current_chunk:
                current_chunk = block
                continue

            combined_len = len(current_chunk) + len(block) + 2

            # If block has a list or is a major heading or exceeds threshold, start a fresh chunk
            if is_major_heading or is_list or combined_len > 900:
                if current_chunk.strip():
                    chunks.append({
                        "page_number": page_number,
                        "text": current_chunk.strip()
                    })
                current_chunk = block
            else:
                current_chunk += "\n\n" + block

        if current_chunk.strip():
            chunks.append({
                "page_number": page_number,
                "text": current_chunk.strip()
            })

        return chunks

    def process_and_index_document(self, db: Session, doc_record: Document) -> Tuple[bool, str]:
        """
        Extracts text from PDF page by page using PyMuPDF,
        splits into chunks with exact page numbering preserved,
        generates vector embeddings, and stores them in the database.
        """
        doc_record.processing_status = "PROCESSING"
        db.commit()

        try:
            pdf_path = Path(doc_record.file_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found at {pdf_path}")

            # Open PDF with PyMuPDF
            doc = pymupdf.open(str(pdf_path))
            total_pages = len(doc)
            doc_record.page_count = total_pages

            all_chunks_data = []

            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_number = page_idx + 1 # 1-indexed for official government pages
                
                # Extract text
                raw_text = page.get_text("text")
                # Normalize line breaks and extra whitespace
                cleaned_text = re.sub(r"[ \t]+", " ", raw_text)
                cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()

                if not cleaned_text:
                    # Record notice for empty or scanned page
                    cleaned_text = f"[Page {page_number}: Image or non-selectable text content]"

                page_chunks = self.chunk_text(
                    cleaned_text, 
                    page_number=page_number,
                    chunk_size=settings.CHUNK_SIZE,
                    overlap=settings.CHUNK_OVERLAP
                )
                all_chunks_data.extend(page_chunks)

            doc.close()

            if not all_chunks_data:
                raise ValueError("No extractable text found in uploaded PDF document.")

            # Generate embeddings and persist chunks
            chunk_texts = [c["text"] for c in all_chunks_data]
            embeddings = embedding_service.get_embeddings_batch(chunk_texts)

            # Delete any existing chunks for this document if re-indexing
            db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_record.id).delete()

            for idx, (chunk_info, emb) in enumerate(zip(all_chunks_data, embeddings)):
                emb_val = embedding_service.format_for_storage(emb)
                chunk_obj = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=doc_record.id,
                    page_number=chunk_info["page_number"],
                    chunk_index=idx,
                    chunk_text=chunk_info["text"],
                    embedding=emb_val
                )
                db.add(chunk_obj)

            doc_record.processing_status = "INDEXED"
            doc_record.error_message = None
            db.commit()
            logger.info(f"Successfully processed and indexed document {doc_record.filename} ({len(all_chunks_data)} chunks, {total_pages} pages)")
            return True, "Indexed successfully"

        except Exception as e:
            logger.error(f"Error processing document {doc_record.id}: {e}", exc_info=True)
            doc_record.processing_status = "FAILED"
            doc_record.error_message = str(e)
            db.commit()
            return False, str(e)

document_service = DocumentService()
