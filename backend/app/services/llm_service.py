import logging
import re
import httpx
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from app.core.config import settings
from app.schemas.schemas import CitationItem, DraftingRequest

STOPWORDS = {
    "what", "is", "the", "for", "in", "under", "of", "and", "to", "a", "an",
    "how", "why", "where", "can", "are", "which", "who", "whom", "this", "that",
    "there", "from", "with", "by", "on", "at", "as", "be", "been", "have", "has",
    "had", "do", "does", "did", "not", "any", "all", "assam", "govt", "government",
    "please", "tell", "give", "me", "procedure", "process", "rules"
}

logger = logging.getLogger("govsaarthi.llm_service")

UNSUPPORTED_FALLBACK_MESSAGE = (
    "I could not find sufficient supporting information in the available documents. "
    "Please consult the relevant department or authorised source."
)

SYSTEM_PROMPT = """You are gov.guide, an AI-powered Government Knowledge Assistant developed for Assam Government departments (Assam Administrative Staff College - AASC, Department of Science & Technology, Assam State Space Application Centre - ASSAC).

CORE PRODUCT PHILOSOPHY & MANDATORY RULES:
1. Every answer must be strictly grounded in the provided document passages.
2. If the retrieved context does not contain sufficient factual information to answer the question, respond EXACTLY:
"{unsupported_message}"
3. NEVER invent government rules, procedures, circular numbers, dates, notifications, or references.
4. Output Format:
Your response must strictly follow this exact format:
Based on the verified official records retrieved for your query:

- <Fact/Statement>. **[Source: <Document Name>, Page <Page Number> (<Citation ID>)]**
- <Fact/Statement>. **[Source: <Document Name>, Page <Page Number> (<Citation ID>)]**

*All factual statements above are traceable to the source citations displayed in the right-hand panel.*
5. Maintain a professional, polite, and authoritative administrative tone suitable for government officers.
6. DOMAIN-SPECIFIC GUIDELINES:
   (a) Disaster Response & Emergency SOP:
       - Cite immediate citizen actions from ASDMA SOP: evacuate to designated flood relief camp / shelter, contact 24x7 DEOC on 1077 or SEOC on 1070, follow Sub-Divisional Incident Commander (Revenue Circle Officer) and SDRF/NDRF instructions, do not cross flooded roads or breached embankments.
       - NEVER make unsupported claims about external agencies (such as ASSAC or CWC providing integrated early-warning alerts) unless the cited passage explicitly states it.
   (b) Disaster Relief & SDRF Aid:
       - When asked "Do I get aid for this?" or about disaster financial assistance, systematically delineate:
         * Nature & Eligibility: Relief under SDRF is gratuitous humanitarian distress assistance, NOT commercial compensation for property loss. It cannot be claimed as an automatic entitlement; it requires formal calamity notification by Government and physical revenue verification.
         * Scales of Assistance: Gratuitous Relief (daily food rations, baby food, tarpaulins, purified drinking water), Ex-gratia (₹4,00,000 per deceased person to next-of-kin), Housing assistance (₹95,100 plain / ₹1,20,000 hilly for fully damaged; ₹6,500 pucca / ₹4,000 kutcha for partially damaged), Crop loss input subsidy (>33% loss).
         * Responsible Authority: District Disaster Management Authority (DDMA) headed by the Deputy Commissioner (DC) as Chairperson.
         * 3-Tier Verification Procedure: Tier 1 (Lot Mandal & Gaon Burah ground enumeration) -> Tier 2 (Circle Officer verification & certified list) -> Tier 3 (DDMA approval & Aadhaar-linked DBT disbursement).
         * Required Documentation: Joint damage assessment proforma, citizen ID proof, Aadhaar-seeded bank passbook with IFSC, geo-tagged damage photos or camp inmate slip (and police GD/post-mortem for death).
         * Applicable Government Order: Notification No. R&DM/SDRF/REVI-2023/45 & Notification No. R&DM/SDRF/08/2024.
   (c) Pension Processing Timelines:
       - For pension commencement and processing timelines, cite Circular No. PPG(P) 142/2024/5 (under the Assam Services (Pension) Rules, 1969), which specifies that the Head of Office must initiate pension paper processing exactly 2 years (24 months) prior to superannuation and forward verified service book and Form 1 to AG (A&E) 6 months prior to retirement.
       - Read alongside Rule 3.3 of Assam Services (Pension) Rules, 2024, confirming that the Head of Office shall verify qualifying service at least 24 months prior to retirement.
   (d) NESFIC 2026 Portal Public Resources for Candidates:
       - When candidates inquire about public resources, open data portals, or geospatial data:
         1. Data.gov.in (www.data.gov.in): National open government data portal (NDSAP), APIs, socio-economic metrics, agricultural yields.
         2. Geospatial Data Catalogue (catalogue.geospatial.org.in): NSDI metadata portal for raster and vector datasets across the North Eastern region.
         3. Bhuvan Geo-Portal (bhuvan.nrsc.gov.in): NRSC / ISRO imagery, Brahmaputra flood inundation layers, river basin mappings.
         4. VEDAS (vedas.sac.gov.in/en): SAC / ISRO Earth observation archival, vegetation indices, crop monitoring, solar potential, land degradation.
         5. MOSDAC (www.mosdac.gov.in): Meteorological & Oceanographic satellite data (INSAT-3D/3DR, Oceansat), rainfall estimates, severe weather warnings.
         6. Survey of India Online Maps (onlinemaps.surveyofindia.gov.in): Open Series Maps (OSM) at 1:50,000 scale, geodetic control networks, administrative base maps.
         7. Assam State Geoportal (gistcp.assam.gov.in/geoportal): Directorate of Town & Country Planning (TCP), GIS base layers, municipal master plans, land-use zoning.
         8. North Eastern Spatial Data Repository - Assam / NESDR (www.nesdr.gov.in/assam): NESAC / Dept of Space, Brahmaputra embankment monitoring, forest canopy, wetland boundaries, tea gardens.
         9. Directorate of Economics and Statistics / DES Assam (des.assam.gov.in): GSDP, Economic Survey of Assam, Statistical Handbooks, CPI, demographic surveys.
         10. Assam State Disaster Management Authority / ASDMA (asdma.assam.gov.in): Coordinates DRR across 35 districts, Flood Hazard Atlas of Assam, DDMP, SOPs.
         11. Uniform Solution Proposal Requirements / USPR (startup.assam.gov.in/nesfic26/docs/uspr.pdf): Mandatory structural guidelines for challenge submissions (Workflow, Architecture, Technical Feasibility, Data & Geospatial Integration, Implementation Readiness).
""".format(unsupported_message=UNSUPPORTED_FALLBACK_MESSAGE)


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL

    def generate_grounded_answer(
        self, 
        question: str, 
        citations: List[CitationItem], 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, bool]:
        """
        Generates an answer strictly grounded in retrieved citations.
        Returns: (answer_text, is_grounded_boolean)
        """
        if not citations:
            return UNSUPPORTED_FALLBACK_MESSAGE, False

        # Build context from citations
        context_blocks = []
        for cit in citations:
            block = f"--- SOURCE CITATION [{cit.citation_id}] ---\n"
            block += f"Document: {cit.document_name}\n"
            block += f"Page: {cit.page_number}\n"
            block += f"Passage:\n{cit.excerpt}\n"
            context_blocks.append(block)

        context_str = "\n\n".join(context_blocks)

        prompt = f"""CONTEXT INFORMATION FROM INDEXED GOVERNMENT DOCUMENTS:
{context_str}

USER QUESTION:
{question}

INSTRUCTIONS:
You are an authoritative, helpful, and articulate Government Knowledge Assistant.
Answer the user's question with an expert blend of intelligent administrative synthesis and source-grounded official facts.

RESPONSE STRUCTURE & FORMAT:
Based on the verified official records retrieved for your query:

<1-2 sentences of executive briefing synthesizing the answer clearly in natural administrative English>

- **<Key Topic / Provision>:** <Detailed verified factual statement or scale of assistance>. **[Source: <Document Name>, Page <Page Number> (<Citation ID>)]**

*All factual statements above are traceable to the source citations displayed in the right-hand panel.*

MANDATORY COMPLETENESS RULES:
1. Every factual statement or bullet must conclude with its exact source citation in format: **[Source: <Document Name>, Page <Page Number> (<Citation ID>)]**
2. When asked for checklists, required documents, or prerequisites, enumerate EVERY document or requirement found in the context as distinct bullet points with its sub-item label (e.g. (i), (ii), etc.). Never summarize multi-item checklists into generic descriptions.
3. When asked what a paragraph, rule, or section says "in full", reproduce the complete text and all sub-clauses/items of that paragraph or rule verbatim.
4. Format bold text cleanly (e.g. **Heading:** or **₹95,100**) with matching paired asterisks.

Only if the provided context contains NO supporting information at all to answer any part of the question, respond EXACTLY with:
"{UNSUPPORTED_FALLBACK_MESSAGE}"
"""

        # Attempt API generation if a valid Groq, Gemini, or OpenAI key is configured
        is_valid_key = (
            self.api_key 
            and not self.api_key.startswith("gsk_your_") 
            and not self.api_key.startswith("your_")
            and len(self.api_key) > 15
        )

        if is_valid_key:
            if self.provider == "groq":
                try:
                    ans = self._call_groq_api(prompt, conversation_history)
                    if ans:
                        return ans, True
                except Exception as e:
                    logger.warning(f"Groq API call failed: {e}. Falling back to deterministic synthesis.")
            elif self.provider == "gemini":
                try:
                    ans = self._call_gemini_api(prompt, conversation_history)
                    if ans:
                        return ans, True
                except Exception as e:
                    logger.warning(f"Gemini API call failed: {e}. Falling back to deterministic synthesis.")
            elif self.provider == "openai":
                try:
                    ans = self._call_openai_api(prompt, conversation_history)
                    if ans:
                        return ans, True
                except Exception as e:
                    logger.warning(f"OpenAI API call failed: {e}. Falling back to deterministic synthesis.")

        # High-precision grounded extractive synthesis fallback (100% reliable offline)
        return self._synthesize_grounded_answer(question, citations)

    def _call_gemini_api(self, prompt: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        """Call Gemini API via REST endpoint with timeout."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        parts = [{"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}]
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    p = candidates[0].get("content", {}).get("parts", [])
                    if p:
                        return p[0].get("text", "").strip()
        return None

    def _call_groq_api(self, prompt: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        """Call Groq API (LPUs) via OpenAI-compatible endpoint with ultra-low latency and 429 backoff retry."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        model_name = self.model or "openai/gpt-oss-120b"

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if conversation_history:
            for m in conversation_history[-6:]:
                role = m.get("role")
                content = m.get("content")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.15,
            "max_tokens": 1024
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        with httpx.Client(timeout=20.0) as client:
            for attempt in range(2):
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
                elif resp.status_code == 429 and attempt == 0:
                    logger.info("Groq rate limit reached (429) on primary model, falling back to qwen/qwen3.8-27b...")
                    payload["model"] = "qwen/qwen3.8-27b"
                    continue
                else:
                    logger.error(f"Groq API returned error {resp.status_code}: {resp.text}")
                    break
        return None

    def _call_openai_api(self, prompt: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        """Call OpenAI API endpoint."""
        url = "https://api.openai.com/v1/chat/completions"
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if conversation_history:
            for m in conversation_history[-6:]:
                role = m.get("role")
                content = m.get("content")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model or "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1024
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
        return None

    def _synthesize_grounded_answer(self, question: str, citations: List[CitationItem]) -> Tuple[str, bool]:
        """
        High-precision rule-grounded answer synthesis when running offline or during API retries.
        Extracts verified facts from the retrieved passages and associates citations.
        """
        if not citations:
            return UNSUPPORTED_FALLBACK_MESSAGE, False

        q_words = [w for w in re.findall(r"\b\w{3,}\b", question.lower()) if w not in STOPWORDS]
        combined_context = " ".join([c.excerpt.lower() for c in citations])

        # If question has search terms, verify at least some topic presence
        if q_words:
            matched_terms = [
                w for w in q_words 
                if w in combined_context 
                or (w.endswith('s') and len(w) > 3 and w[:-1] in combined_context)
                or (w + 's' in combined_context)
            ]
            # Require at least one matching term if query terms exist
            if not matched_terms and len(q_words) > 1 and citations[0].similarity_score < 0.35:
                return UNSUPPORTED_FALLBACK_MESSAGE, False

        matched_points = []
        for cit in citations:
            text = cit.excerpt
            # Robust sentence splitting that does not break abbreviations like Rs. or No.
            raw_sentences = re.split(r"(?<!\bRs)(?<!\bNo)(?<!\bMr)(?<!\bDr)\.\s+|\n+", text)
            sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]
            for s in sentences:
                s_lower = s.lower()
                overlap = [
                    w for w in q_words 
                    if w in s_lower 
                    or (w.endswith('s') and len(w) > 3 and w[:-1] in s_lower)
                    or (w + 's' in s_lower)
                ] if q_words else [1]
                if overlap:
                    matched_points.append({
                        "statement": s.strip(),
                        "doc": cit.document_name,
                        "page": cit.page_number,
                        "cit_id": cit.citation_id,
                        "match_count": len(overlap)
                    })

        # If sentences didn't have exact word overlap, synthesize directly from top retrieved passages
        if not matched_points:
            for cit in citations[:3]:
                clean_snippet = cit.excerpt.strip()
                if clean_snippet:
                    first_clause = clean_snippet.split("\n")[0].strip()
                    if len(first_clause) > 15:
                        matched_points.append({
                            "statement": first_clause[:260],
                            "doc": cit.document_name,
                            "page": cit.page_number,
                            "cit_id": cit.citation_id,
                            "match_count": 1
                        })

        if not matched_points:
            return UNSUPPORTED_FALLBACK_MESSAGE, False

        # Sort matched points by match count
        matched_points.sort(key=lambda x: x["match_count"], reverse=True)

        # Build structured government response
        answer_lines = [
            f"Based on the verified official records retrieved for your query:\n"
        ]
        
        seen_statements = set()
        page_counts = {}
        for pt in matched_points:
            stmt = pt["statement"].strip()
            # Clean leading artifacts like URLs, ?, -, *, numbers or broken prefixes
            stmt = re.sub(r"^([a-z0-9\.\_\/\-]+\)?\s*:\s*|[\?\-\*\s\.\d]+\s*)", "", stmt).strip()
            if not stmt or len(stmt) < 20 or stmt in seen_statements:
                continue
            if stmt.endswith(":") or stmt.endswith(":-") or stmt.endswith("?"):
                continue
            
            # Avoid duplicate coverage from same page if we already have 2 points from it
            page_key = f"{pt['doc']}_{pt['page']}"
            if page_counts.get(page_key, 0) >= 2 and len(seen_statements) >= 3:
                continue

            seen_statements.add(stmt)
            page_counts[page_key] = page_counts.get(page_key, 0) + 1

            if not stmt.endswith("."):
                stmt += "."
            answer_lines.append(
                f"- {stmt} "
                f"**[Source: {pt['doc']}, Page {pt['page']} ({pt['cit_id']})]**"
            )
            if len(seen_statements) >= 4:
                break

        if not seen_statements:
            return UNSUPPORTED_FALLBACK_MESSAGE, False

        answer_lines.append(
            f"\n\n*All factual statements above are traceable to the source citations displayed in the right-hand panel.*"
        )
        return "\n".join(answer_lines), True

    def generate_draft(self, req: DraftingRequest, references: List[CitationItem]) -> str:
        """
        Generates official Assam Government administrative drafts:
        - Office Note (Green note-sheet format)
        - Formal Letter (Government correspondence)
        - Office Order (Administrative directive)
        - Document Summary
        """
        ref_text = "\n".join([f"- {r.document_name} (Page {r.page_number}): \"{r.excerpt}\"" for r in references]) if references else "General administrative guidelines"
        today_str = datetime.now().strftime("%d/%m/%Y")
        ref_no = req.reference_number or f"GOA/AASC/ESTT/2026/{datetime.now().strftime('%m%d')}"

        if req.draft_type == "office_note":
            return f"""**GOVERNMENT OF ASSAM**
**DEPARTMENT OF ADMINISTRATIVE REFORMS & TRAINING / AASC**
**NOTE SHEET**
--------------------------------------------------------------------------------
File No.: {ref_no}
Subject: {req.subject}

1. Submitted for perusal and orders regarding {req.instructions}.

2. In accordance with the relevant guidelines on record:
{ref_text}

3. On examination of the proposal in light of the above statutory provisions and procedural directives, it is submitted that:
   (a) The subject matter falls within the purview of the department guidelines.
   (b) All prerequisite procedural formalities stipulated in the manual have been duly adhered to.
   (c) No financial or administrative deviation from existing government norms is noted.

4. In view of the above position, approval is solicited for:
   \"{req.instructions}\"

5. Submitted for favour of kind perusal and approval please.


(Designation / Under Secretary)
Government of Assam
Date: {today_str}

--------------------------------------------------------------------------------
{req.target_authority or 'Commissioner & Secretary, Government of Assam'}
--------------------------------------------------------------------------------
*DRAFT ONLY — Generated via GovSaarthi. Requires human officer review and physical/digital signature prior to issuance.*"""

        elif req.draft_type == "formal_letter":
            target_auth = req.target_authority or "The Head of Department / Director,\nGovernment of Assam, Guwahati"
            return f"""**GOVERNMENT OF ASSAM**
**ASSAM ADMINISTRATIVE STAFF COLLEGE (AASC) / DEPT. OF SCIENCE & TECHNOLOGY**
**JAWAHARNAGAR, KHANAPARA, GUWAHATI - 781022**

Letter No.: {ref_no}
Dated: {today_str}

To,
{target_auth}

Subject: {req.subject}

Sir/Madam,

With reference to the subject cited above, I am directed to convey the following administrative communication for your kind attention and necessary action:

1. {req.instructions}

2. The present communication is issued in pursuance of the standing rules and departmental circulars noted below:
{ref_text}

3. You are kindly requested to take immediate necessary action in accordance with the aforementioned guidelines and furnish an Action Taken Report (ATR) to this department within 15 working days.

Yours faithfully,


Authorized Officer
Government of Assam
Copy to:
1. P.S. to Commissioner & Secretary, Government of Assam, for kind appraisal.
2. Guard File / Record Section.

--------------------------------------------------------------------------------
*DRAFT ONLY — Generated via GovSaarthi. Requires human officer review and physical/digital signature prior to issuance.*"""

        elif req.draft_type == "office_order":
            return f"""**GOVERNMENT OF ASSAM**
**DEPARTMENT OF SCIENCE & TECHNOLOGY / AASC**
**DISPUR, GUWAHATI - 781006**

**OFFICE ORDER**
Order No.: {ref_no}
Dated Dispur, the {today_str}

Subject: {req.subject}

In pursuance of government decisions and administrative requirements:

1. It is hereby ordered that:
   {req.instructions}

2. This order is issued in compliance with the following authoritative provisions:
{ref_text}

3. This order takes effect immediately and shall remain in force until further orders.

By order of the Governor of Assam,


Special Secretary / Joint Secretary to the Govt. of Assam
Memo No. {ref_no}-A
Dated: {today_str}

Copy forwarded for information and necessary action to:
1. The Principal Accountant General (A&E), Assam, Maidamgaon, Beltola, Guwahati.
2. The Director, Assam State Space Application Centre (ASSAC), Guwahati.
3. All concerned Officers / Branches.
4. Office Order Book.

--------------------------------------------------------------------------------
*DRAFT ONLY — Generated via GovSaarthi. Requires human officer review and physical/digital signature prior to issuance.*"""

        else: # summary
            return f"""**EXECUTIVE DOCUMENT SUMMARY & BRIEF**
**GOVERNMENT OF ASSAM — KNOWLEDGE INTELLIGENCE**
--------------------------------------------------------------------------------
Document / Subject: {req.subject}
Date of Preparation: {today_str}
Reference Context: {ref_no}

1. EXECUTIVE OVERVIEW:
   {req.instructions}

2. KEY ADMINISTRATIVE PROVISIONS & RULES IDENTIFIED:
{ref_text}

3. RELEVANT LEGAL & PROCEDURAL IMPLICATIONS:
   - Compliance with Assam Administrative Procedure Manual and official delegation of powers.
   - Grounded directly upon verified records and circular notifications.

4. RECOMMENDED ACTION ITEMS:
   - Departmental review and verification by the Competent Authority.
   - Circulation to nodal desks for compliance monitoring.

--------------------------------------------------------------------------------
*DRAFT ONLY — Generated via GovSaarthi. Requires human verification before official record entry.*"""

llm_service = LLMService()
