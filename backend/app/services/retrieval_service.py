import logging
import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import IS_POSTGRES, PG_VECTOR_AVAILABLE
from app.models.models import Document, DocumentChunk
from app.schemas.schemas import CitationItem
from app.services.embedding_service import embedding_service
from app.services.validation_service import validation_service

STOPWORDS = {
    "what", "is", "the", "for", "in", "under", "of", "and", "to", "a", "an",
    "how", "why", "where", "can", "are", "which", "who", "whom", "this", "that",
    "there", "from", "with", "by", "on", "at", "as", "be", "been", "have", "has",
    "had", "do", "does", "did", "not", "any", "all", "assam", "govt", "government"
}

logger = logging.getLogger("govsaarthi.retrieval_service")

DOMAIN_SYNONYMS = {
    "pension": ["superannuation", "retirement", "ppo", "pensioner"],
    "pensions": ["superannuation", "retirement", "ppo", "pensioner"],
    "pensioner": ["superannuation", "retirement", "pension"],
    "superannuation": ["pension", "retirement", "relieving"],
    "retire": ["superannuation", "pension", "relieving", "retirement"],
    "retirement": ["superannuation", "pension", "relieving"],
    "flood": ["inundation", "brahmaputra", "asdma", "hazard", "embankment", "disaster"],
    "floods": ["inundation", "brahmaputra", "asdma", "hazard", "embankment", "disaster"],
    "disaster": ["flood", "calamity", "sdrf", "hazard", "asdma", "relief", "evacuation"],
    "aid": ["relief", "assistance", "sdrf", "compensation", "grant", "gratuitous"],
    "relief": ["aid", "assistance", "sdrf", "gratuitous", "grant"],
    "assistance": ["relief", "aid", "sdrf", "grant", "subsidy"],
    "damage": ["loss", "breach", "damaged", "destroyed", "compensation"],
    "compensation": ["relief", "assistance", "ex-gratia", "sdrf", "aid"],
    "satellite": ["remote sensing", "bhuvan", "assac", "isro", "earth observation"],
    "gis": ["geospatial", "spatial", "mapping", "geoportal", "cadastral"],
    "geospatial": ["gis", "spatial", "mapping", "geoportal"],
    "spatial": ["geospatial", "gis", "mapping", "geoportal"],
    "proposal": ["uspr", "nesfic", "component", "challenge", "requirements"],
    "uspr": ["proposal", "nesfic", "guidelines", "format", "requirements"],
    "resources": ["portals", "datasets", "geospatial", "nesfic", "open data", "public resources"],
    "portal": ["data.gov.in", "bhuvan", "geoportal", "nesdr", "repository", "vedas", "mosdac"],
    "catalogue": ["geospatial", "nsdi", "metadata", "thematic", "raster"],
    "statistics": ["des", "gsdp", "economic survey", "handbook", "cpi"],
    "economic": ["gsdp", "des", "survey", "demographic", "statistics"],
    "survey": ["geodetic", "1:50,000", "osm", "mapping", "survey of india"],
    "maps": ["osm", "1:50,000", "survey of india", "geoportal", "cadastral"],
    "weather": ["mosdac", "meteorological", "rainfall", "insat", "oceanographic"],
    "meteorological": ["mosdac", "rainfall", "forecast", "cloud", "insat"],
    "vegetation": ["vedas", "sac", "isro", "crop", "indices"],
    "manual": ["secretariat", "procedure", "notesheet", "office procedure"],
    "training": ["aasc", "induction", "in-service", "pedagogy", "curriculum"],
    "rules": ["circular", "notification", "memorandum", "act", "manual", "rule", "provision"],
    "paragraph": ["para", "section", "clause", "rule", "provision"],
    "paragraphs": ["para", "paras", "section", "clause", "rule"],
    "para": ["paragraph", "section", "clause", "rule", "provision"],
    "paras": ["paragraphs", "section", "clause", "rule"],
    "rule": ["rules", "section", "para", "paragraph", "clause", "circular", "notification"],
    "provision": ["rule", "section", "para", "paragraph", "clause", "guideline", "deadline"],
    "provisions": ["rules", "sections", "paras", "paragraphs", "clauses"],
    "checklist": ["documents", "records", "required", "mandatory", "items", "form"],
    "checklists": ["documents", "records", "required", "mandatory", "items"],
    "documents": ["checklist", "records", "application", "dossier", "papers", "required"],
    "document": ["checklist", "record", "application", "dossier", "paper", "required"],
    "deadline": ["timeline", "months", "schedule", "period", "superannuation", "deadline"],
    "deadlines": ["timelines", "months", "schedule", "period"],
    "timeline": ["deadline", "months", "schedule", "period", "superannuation"],
    "timelines": ["deadlines", "months", "schedule", "period"],
    "incomplete": ["missing", "reconstruct", "reconstruction", "provisional"],
    "authority": ["sanctioning", "forwarding", "appointing", "head of office", "hoo", "accountant general"],
    "forwards": ["forwarding", "transmit", "submission", "submit", "head of office"],
    "forwarding": ["forwards", "transmit", "submission", "submit", "head of office"]
}

class RetrievalService:
    def __init__(self):
        self.top_k = settings.TOP_K_CHUNKS
        self.similarity_threshold = settings.RELEVANCE_SIMILARITY_THRESHOLD

    def retrieve_relevant_chunks(
        self, 
        db: Session, 
        query: str, 
        document_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[CitationItem]:
        """
        Retrieves top relevant chunks using pgvector (if available) or numpy cosine search.
        Applies domain boundary filters to prevent cross-domain hallucination.
        Applies similarity threshold and joins with parent Document metadata to return citations.
        """
        k = top_k or max(self.top_k, 7)
        thresh = threshold if threshold is not None else self.similarity_threshold
        query_embedding = embedding_service.get_embedding(query, is_query=True)

        # Domain boundary determination to prevent cross-domain contamination
        allowed_docs = None
        if not document_id:
            domain = validation_service.classify_query_domain(query, conversation_history)
            if domain:
                allowed_docs = validation_service.get_allowed_documents_for_domain(domain)
                logger.info(f"Query classified into domain '{domain}' with {len(allowed_docs)} allowed docs: {allowed_docs}")
                # When hard domain restriction is active, relax threshold slightly to capture authentic domain clauses
                if threshold is None:
                    thresh = min(thresh, 0.15)

        results: List[Dict[str, Any]] = []

        if PG_VECTOR_AVAILABLE:
            # Native pgvector cosine distance query (<=> operator)
            # cosine similarity = 1 - cosine distance
            try:
                filter_clause = "WHERE d.processing_status = 'INDEXED'"
                params = {"query_emb": str(query_embedding), "k": k}
                if document_id:
                    filter_clause += " AND d.id = :doc_id"
                    params["doc_id"] = document_id
                elif allowed_docs:
                    placeholders = ", ".join([f":ad_{i}" for i in range(len(allowed_docs))])
                    filter_clause += f" AND d.filename IN ({placeholders})"
                    for i, doc_name in enumerate(allowed_docs):
                        params[f"ad_{i}"] = doc_name

                sql = f"""
                    SELECT 
                        c.id as chunk_id,
                        c.document_id,
                        d.filename as document_name,
                        c.page_number,
                        c.chunk_text,
                        1 - (c.embedding <=> cast(:query_emb as vector)) as similarity
                    FROM document_chunks c
                    JOIN documents d ON c.document_id = d.id
                    {filter_clause}
                    ORDER BY c.embedding <=> cast(:query_emb as vector)
                    LIMIT :k
                """
                cursor = db.execute(text(sql), params)
                for row in cursor.fetchall():
                    similarity = float(row.similarity)
                    if similarity >= thresh:
                        results.append({
                            "chunk_id": row.chunk_id,
                            "document_id": row.document_id,
                            "document_name": row.document_name,
                            "page_number": row.page_number,
                            "chunk_text": row.chunk_text,
                            "similarity": similarity
                        })
            except Exception as e:
                db.rollback()
                logger.warning(f"pgvector query failed, using in-memory retrieval fallback: {e}")
                results = self._fallback_in_memory_retrieval(db, query, query_embedding, document_id, allowed_docs, k, thresh)
        else:
            results = self._fallback_in_memory_retrieval(db, query, query_embedding, document_id, allowed_docs, k, thresh)

        # Deduplicate retrieved chunks by (document_id, page_number)
        # Groups multiple chunks from the exact same document page into one consolidated citation
        # while merging their text so no supporting information or checklist item is lost.
        unique_results: List[Dict[str, Any]] = []
        seen_doc_pages: Dict[Any, Dict[str, Any]] = {}
        for res in results:
            key = (res["document_id"], res["page_number"])
            if key not in seen_doc_pages:
                entry = dict(res)
                seen_doc_pages[key] = entry
                unique_results.append(entry)
            else:
                existing = seen_doc_pages[key]
                # Merge chunk text cleanly if not already contained
                if res["chunk_text"] not in existing["chunk_text"]:
                    existing["chunk_text"] = existing["chunk_text"].rstrip() + "\n\n" + res["chunk_text"].lstrip()
                if res["similarity"] > existing["similarity"]:
                    existing["similarity"] = res["similarity"]

        # Build CitationItem objects
        citations: List[CitationItem] = []
        for idx, res in enumerate(unique_results[:k]):
            text_snippet = self._extract_clean_excerpt(res["chunk_text"], query)
            citation = CitationItem(
                citation_id=f"CIT-{idx + 1}",
                document_id=res["document_id"],
                document_name=res["document_name"],
                page_number=res["page_number"],
                excerpt=text_snippet,
                similarity_score=round(res["similarity"], 4)
            )
            citations.append(citation)

        return citations

    def _fallback_in_memory_retrieval(
        self, 
        db: Session, 
        query: str, 
        query_embedding: List[float], 
        document_id: Optional[str], 
        allowed_docs: Optional[List[str]],
        k: int, 
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Vector retrieval over indexed document chunks using hybrid vector + lexical keyword scoring."""
        query_obj = db.query(DocumentChunk, Document.filename).join(
            Document, DocumentChunk.document_id == Document.id
        ).filter(Document.processing_status == "INDEXED")

        if document_id:
            query_obj = query_obj.filter(Document.id == document_id)
        elif allowed_docs:
            query_obj = query_obj.filter(Document.filename.in_(allowed_docs))

        all_chunks = query_obj.all()
        scored_chunks = []

        query_terms = [t.lower() for t in re.findall(r"\b\w{3,}\b", query) if t.lower() not in STOPWORDS]
        # Expand domain synonyms for broader administrative comprehension
        expanded_terms = set(query_terms)
        for term in query_terms:
            if term in DOMAIN_SYNONYMS:
                expanded_terms.update(DOMAIN_SYNONYMS[term])

        # Specialized administrative patterns in user query
        para_matches = re.findall(r"\b(?:para|paragraph)\s*(\d+)\b", query, re.I)
        rule_matches = re.findall(r"\b(?:rule|section)\s*(\d+(?:\.\d+)?)\b", query, re.I)
        circ_matches = re.findall(r"\b(?:circular|no\.?)\s*(\d+)\b", query, re.I)
        is_list_query = bool(re.search(r"\b(list|every\s+document|documents?\s+required|checklist|mandatory\s+documents|what\s+documents|prerequisite|forms?)\b", query, re.I))
        has_deadline = bool(re.search(r"\b(six[\s\-]month|6[\s\-]month|deadline|timeline|commence|forwarding|authority)\b", query, re.I))

        for chunk, filename in all_chunks:
            if not chunk.embedding:
                continue
            chunk_vec = embedding_service.parse_from_storage(chunk.embedding)
            sim = embedding_service.cosine_similarity(query_embedding, chunk_vec)
            
            # Hybrid lexical boost: reward occurrences of domain-specific query terms & synonyms
            text_lower = chunk.chunk_text.lower()
            term_matches = sum(
                1 for term in expanded_terms 
                if term in text_lower 
                or (term.endswith('s') and len(term) > 3 and term[:-1] in text_lower)
                or (term + 's' in text_lower)
            )
            boost = min(0.40, term_matches * 0.08) if term_matches > 0 else 0.0

            # Boost for explicit paragraph references (e.g. "paragraph 2" -> "para 2")
            if para_matches:
                for p_num in para_matches:
                    if f"para {p_num}" in text_lower or f"para {p_num}:" in text_lower or f"paragraph {p_num}" in text_lower or f"para {p_num} -" in text_lower:
                        boost += 0.50

            # Boost for explicit rule/section references (e.g. "rule 3.2" or "rule 3")
            if rule_matches:
                for r_num in rule_matches:
                    if f"rule {r_num}" in text_lower or f"section {r_num}" in text_lower or f"{r_num} " in text_lower:
                        boost += 0.45

            # Boost for circular references
            if circ_matches:
                for c_num in circ_matches:
                    if f"circular" in text_lower and c_num in text_lower:
                        boost += 0.40

            # Boost chunks containing structured checklists when the query requests a list or required documents
            if is_list_query:
                if re.search(r"\((?:i|ii|iii|iv|v|vi|vii|viii|a|b|c|d|1|2|3)\)", text_lower):
                    boost += 0.35

            # Boost chunks containing timeline / forwarding clauses when requested
            if has_deadline:
                if "six months" in text_lower or "six-month" in text_lower or "24 months" in text_lower or "two years" in text_lower or "forwarding authority" in text_lower:
                    boost += 0.35

            # If query has specific search keywords and NONE match this chunk, dampen score
            if query_terms and term_matches == 0 and not (para_matches or rule_matches):
                combined_score = sim * 0.50
            else:
                combined_score = sim + boost

            if combined_score >= threshold:
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_name": filename,
                    "page_number": chunk.page_number,
                    "chunk_text": chunk.chunk_text,
                    "similarity": combined_score
                })

        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:k]

    def _extract_clean_excerpt(self, full_chunk_text: str, query: str) -> str:
        """
        Extract a clear, complete, and uncorrupted excerpt for LLM context and user inspection.
        Preserves full checklists, sub-items (i)-(viii), and rule structures up to 2000 chars.
        """
        text = full_chunk_text.strip()
        if len(text) <= 2000:
            return text
        
        # If chunk is extremely long (>2000 chars), take the most informative 2000 characters
        return text[:2000] + "..."

retrieval_service = RetrievalService()
