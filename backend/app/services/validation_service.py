import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.models import Document
from app.schemas.schemas import CitationItem

logger = logging.getLogger("govsaarthi.validation_service")

UNSUPPORTED_FALLBACK_MESSAGE = (
    "I could not find sufficient supporting information in the available documents. "
    "Please consult the relevant department or authorised source."
)

# Domain Regex Patterns for Multi-Format Question Classification
DOMAIN_PATTERNS: Dict[str, List[str]] = {
    "disaster": [
        r"\bdisaster\b", r"\bflood(s|ing)?\b", r"\brelief\b", r"\baid\b", r"\bsdrf\b",
        r"\brescue\b", r"\bshelter(s)?\b", r"\bevacuat(e|ion|ed)\b", r"\bcamp(s)?\b",
        r"\bdamage(s|d)?\b", r"\binundat(ed|ion)\b", r"\bbreach\b", r"\bembankment(s)?\b",
        r"\bddma\b", r"\basdma\b", r"\berosion\b", r"\bcalamity\b", r"\bex-gratia\b",
        r"\bmarooned\b", r"\bgaon\s+burah\b", r"\blot\s+mandal\b"
    ],
    "pension": [
        r"\bpension(s|er|ers)?\b", r"\bsuperannuat(ion|ed)?\b", r"\bretire(d|ment)?\b",
        r"\bppo\b", r"\bdcrg\b", r"\bgratuity\b", r"\bservice\s+book\b",
        r"\bqualifying\s+service\b", r"\bcircular\s+(no\.?\s*)?142\b", r"\bform\s+1\b",
        r"\bprovisional\s+pension\b", r"\bno\s+dues\b", r"\blast\s+pay\b",
        r"\bparagraph\s*2\b", r"\bpara\s*2\b", r"\brule\s*3(\.\d+)?\b",
        r"\b(six|6)[\s\-]month\b", r"\b(two|2)[\s\-]year\b", r"\b24[\s\-]month\b",
        r"\bhead\s+of\s+office\b", r"\bhoo\b", r"\bforward(ing|s)?\b",
        r"\bdeadline(s)?\b", r"\btimeline(s)?\b", r"\bchecklist\b"
    ],
    "secretariat": [
        r"\bsecretariat\b", r"\bdak\b", r"\bdiaris(ation|e|ed)\b", r"\bnote\s+sheet(s)?\b",
        r"\bgreen\s+note\b", r"\bfile\s+movement\b", r"\boffice\s+procedure\b",
        r"\bcentral\s+diarising\b", r"\burgent\s+slip\b"
    ],
    "training": [
        r"\btraining\b", r"\baasc\b", r"\bin-service\b", r"\binduction\b",
        r"\bdisciplinary\b", r"\brule\s+9\b", r"\bpenalty\b", r"\bapar\b",
        r"\bcapacity\s+building\b"
    ],
    "geospatial": [
        r"\bremote\s+sensing\b", r"\bsatellite(s)?\b", r"\bgis\b", r"\bassac\b",
        r"\bbhuvan\b", r"\bvedas\b", r"\bmosdac\b", r"\bdrone(s)?\b", r"\bgeoportal\b",
        r"\bsurvey\s+of\s+india\b", r"\bdem\b", r"\belevation\s+model\b", r"\bagdi\b",
        r"\bwgs84\b", r"\butm\b", r"\bdata\.gov\.in\b", r"\bgeospatial\s+data\s+catalogue\b",
        r"\bnsdi\b", r"\bnesdr\b", r"\bonlinemaps\b", r"\b1:50,000\b",
        r"\bgistcp\b", r"\btown\s+(&|and)\s+country\s+planning\b",
        r"\bdirectorate\s+of\s+economics\b", r"\bdes(\.assam)?\b", r"\bgsdp\b",
        r"\beconomic\s+survey\b", r"\bstatistical\s+handbook\b"
    ],
    "nesfic_proposal": [
        r"\bproposal\b", r"\buspr\b", r"\bnesfic\b", r"\bchallenge\b",
        r"\bassessment\s+dimension\b", r"\bproblem\s+fit\b", r"\bpilot\s+validation\b",
        r"\bstream\s+1\b", r"\bnesfic-d-36\b", r"\bpublic\s+resources?\b",
        r"\bportal\s+resources?\b", r"\bcandidates?\b", r"\bchallenge\s+solutions?\b",
        r"\bresearch\s+context\b", r"\bopen\s+data\b"
    ]
}

# Domain to Document Filename Mappings (Hard Domain Boundary Enforcement)
DOMAIN_DOCUMENT_MAPPING: Dict[str, List[str]] = {
    "disaster": [
        "ASDMA_Disaster_Management_SOP_and_Relief_Manual.pdf"
    ],
    "pension": [
        "Assam Pension Rules, 2024.pdf",
        "Assam_Pension_Rules_Circular_No_142.pdf",
        "Pension Processing Guidelines (OM).pdf"
    ],
    "secretariat": [
        "Assam_Secretariat_Manual_of_Office_Procedure.pdf"
    ],
    "training": [
        "AASC_State_Training_Policy_Guidelines.pdf"
    ],
    "geospatial": [
        "DST_ASSAC_Remote_Sensing_Notification.pdf",
        "NESFIC_2026_Official_State_Geospatial_and_Open_Data_Resources.pdf"
    ],
    "nesfic_proposal": [
        "Uniform_Solution_Proposal_Requirements_(USPR).pdf",
        "NESFIC_2026_Official_State_Geospatial_and_Open_Data_Resources.pdf"
    ]
}

class ValidationService:
    def classify_query_domain(
        self, 
        query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[str]:
        """Classify user query into its dominant administrative or technical domain."""
        q_low = query.lower()
        # Count matches for each domain
        scores: Dict[str, int] = {}
        for dom, patterns in DOMAIN_PATTERNS.items():
            count = sum(1 for p in patterns if re.search(p, q_low))
            if count > 0:
                scores[dom] = count

        if scores:
            return max(scores, key=lambda k: scores[k])

        # If query alone didn't match, check recent conversation history
        if conversation_history:
            for msg in reversed(conversation_history[-4:]):
                content = (msg.get("content") or "").lower()
                hist_scores: Dict[str, int] = {}
                for dom, patterns in DOMAIN_PATTERNS.items():
                    cnt = sum(1 for p in patterns if re.search(p, content))
                    if cnt > 0:
                        hist_scores[dom] = cnt
                if hist_scores:
                    return max(hist_scores, key=lambda k: hist_scores[k])

        return None

    def get_allowed_documents_for_domain(self, domain: Optional[str]) -> Optional[List[str]]:
        """Return list of allowed document filenames for a classified domain."""
        if not domain or domain not in DOMAIN_DOCUMENT_MAPPING:
            return None
        return DOMAIN_DOCUMENT_MAPPING[domain]

    def validate_and_filter_claims(
        self, 
        answer_text: str, 
        citations: List[CitationItem]
    ) -> Tuple[str, bool]:
        """
        Claim-to-Source Validation Step:
        1. Parses each bullet / claim generated.
        2. Validates that the cited document and page exist in retrieved citations.
        3. Verifies that the factual assertions in the claim are grounded in the cited passage.
        4. Strips unsupported claims or hallucinated references.
        5. Returns validated formatted answer and grounded status.
        """
        if not answer_text or answer_text.strip() == UNSUPPORTED_FALLBACK_MESSAGE:
            return UNSUPPORTED_FALLBACK_MESSAGE, False

        # Normalize unicode hyphens / dashes
        norm_text = re.sub(r"[\u2010-\u2015\u2212]", "-", answer_text)

        lines = norm_text.split("\n")
        valid_claims: List[str] = []
        citation_map = {re.sub(r"[\u2010-\u2015\u2212]", "-", c.citation_id).upper(): c for c in citations}
        # Also map by (doc_name_clean, page_number) and doc_name
        doc_page_map = {}
        doc_map = {}
        for c in citations:
            doc_map[c.document_name.lower()] = c
            doc_page_map[(c.document_name.lower(), c.page_number)] = c

        source_regex = re.compile(
            r"(?:\*\*)?\s*\[Source:\s*([^,\]]+),\s*Page\s*(\d+)(?:\s*\(([^)]+)\))?\]\s*(?:\*\*)?", 
            re.IGNORECASE
        )

        # Standard recognized entities by domain to prevent false positives on known state bodies
        domain_recognized_entities = {
            "disaster": {"ASDMA", "DDMA", "SDRF", "NDRF", "DEOC", "SEOC", "DBT", "PWD", "FIR"},
            "pension": {"PPO", "DCRG", "AG", "PPG", "NOC", "LPC"},
            "secretariat": {"DAK", "SOP"},
            "geospatial": {"ASSAC", "ISRO", "NRSC", "SAC", "NESAC", "NESDR", "GIS", "GPS", "DEM", "OSM", "NSDI", "NDSAP", "DES", "GSDP", "CPI", "TCP"},
            "training": {"AASC", "APAR"},
            "nesfic_proposal": {"USPR", "ASDMA", "ASSAC", "ISRO", "NRSC", "SAC", "NESAC", "NESDR", "DES", "GSDP"}
        }

        # Extract introductory briefing from the text before the first bullet/claim
        first_bullet_match = re.search(r"\n\s*(?:[\-\*\•]|\d+\.)\s+", norm_text)
        intro_briefing = ""
        cursor = 0
        if first_bullet_match:
            raw_intro = norm_text[:first_bullet_match.start()].strip()
            raw_intro = re.sub(r"^Based on the verified official records[^\n]*\n*", "", raw_intro, flags=re.IGNORECASE).strip()
            if len(raw_intro) > 15:
                intro_briefing = raw_intro
            cursor = first_bullet_match.start()
        else:
            preamble_match = re.search(r"Based on the verified official records[^\n]*\n*", norm_text, re.IGNORECASE)
            cursor = preamble_match.end() if preamble_match else 0

        # Extract claim units ending with a source citation starting after the introductory text
        matches = list(source_regex.finditer(norm_text))
        claim_units: List[str] = []
        if matches:
            cur_pos = cursor
            for m in matches:
                if m.start() < cursor:
                    continue
                unit = norm_text[cur_pos:m.end()].strip()
                unit = re.sub(r"\*+All factual statements above[^\n]*\*+", "", unit).strip()
                if unit:
                    claim_units.append(unit)
                cur_pos = m.end()
        else:
            claim_units = [l.strip() for l in norm_text[cursor:].split("\n") if l.strip()]

        for unit in claim_units:
            trimmed = unit.strip()
            if not trimmed:
                continue

            # Find cited source
            match = source_regex.search(trimmed)
            if not match:
                # If no source tag exists on this claim, skip
                continue

            doc_name_raw = match.group(1).strip()
            page_num_str = match.group(2).strip()
            page_num = int(page_num_str) if page_num_str.isdigit() else 1
            cit_id_raw = match.group(3).strip() if match.group(3) else None
            cit_id_clean = re.sub(r"[\u2010-\u2015\u2212]", "-", cit_id_raw).upper() if cit_id_raw else None

            # Find matching citation
            matching_cit: Optional[CitationItem] = None
            if cit_id_clean and cit_id_clean in citation_map:
                matching_cit = citation_map[cit_id_clean]
            else:
                # Try matching by (doc_name, page_num)
                for (dname, pnum), c in doc_page_map.items():
                    if (dname in doc_name_raw.lower() or doc_name_raw.lower() in dname) and pnum == page_num:
                        matching_cit = c
                        break
                if not matching_cit:
                    for k, v in doc_map.items():
                        if k in doc_name_raw.lower() or doc_name_raw.lower() in k:
                            matching_cit = v
                            break

            if not matching_cit:
                logger.warning(f"Validation failed: Cited document '{doc_name_raw}' not found in retrieved citations.")
                continue

            # Grounding check: verify that key factual words of the claim exist in the supporting passage
            claim_body = source_regex.sub("", trimmed).strip()
            # Strip leading list markers (- or • or * or 1.) without touching bold ** asterisks
            claim_body = re.sub(r"^\s*(?:[\-\•]|\*(?!\*)|(?:\d+\.))\s+", "", claim_body).strip()
            claim_body = re.sub(r"[\s\.]+$", "", claim_body).strip()

            passage_lower = matching_cit.excerpt.lower()

            # Proper noun / agency hallucination check:
            # If the claim introduces specific external agencies or acronyms (e.g., CWC, ASSAC in disaster),
            # that acronym/agency MUST either be a standard recognized entity for the domain or appear in the cited passage/doc.
            acronyms = set(re.findall(r"\b[A-Z]{3,}\b", claim_body))
            common_uppercase = {"NOTE", "STEP", "FORM", "PAGE", "PART", "RULE", "PARA", "FREE", "DATE", "NAME", "HEAD", "TOTAL", "CASE", "DEPT", "GOVT"}
            
            # Identify current domain
            active_domain = self.classify_query_domain(claim_body)
            known_domain_entities = domain_recognized_entities.get(active_domain, set()) if active_domain else set()

            unsupported_acronyms = [
                a for a in acronyms 
                if a not in common_uppercase 
                and a not in known_domain_entities
                and a.lower() not in passage_lower 
                and a.lower() not in matching_cit.document_name.lower()
            ]
            if unsupported_acronyms:
                logger.warning(
                    f"Validation rejected claim due to unsupported agency/acronyms {unsupported_acronyms}: '{claim_body[:60]}...'"
                )
                continue

            # Extract key nouns/terms (length > 3, alphanumeric)
            claim_words = [w.lower() for w in re.findall(r"\b[A-Za-z0-9\-\/]{4,}\b", claim_body)]
            
            # Filter common stop words from verification
            content_words = [
                w for w in claim_words 
                if w not in {"with", "that", "this", "from", "shall", "under", "must", "have", "been", "will", "such", "duly", "per", "case"}
            ]

            if content_words:
                matches_cnt = sum(1 for w in content_words if w in passage_lower or (w.endswith('s') and w[:-1] in passage_lower))
                overlap_ratio = matches_cnt / len(content_words)
                # Claim must have at least 20% verified grounding overlap or at least 2 content terms
                if matches_cnt < 2 and overlap_ratio < 0.20:
                    logger.warning(f"Validation failed: Claim '{claim_body[:60]}...' lacks grounding in passage ({matches_cnt}/{len(content_words)} matches).")
                    continue

            # Clean and standardize claim
            std_cit_tag = f"**[Source: {matching_cit.document_name}, Page {matching_cit.page_number} ({matching_cit.citation_id})]**"
            clean_statement = claim_body.rstrip(". ")
            if "\n" in clean_statement:
                valid_claims.append(f"- {clean_statement} {std_cit_tag}")
            else:
                valid_claims.append(f"- {clean_statement}. {std_cit_tag}")

        if not valid_claims:
            logger.warning("Claim-to-source validation: No claims passed verification. Returning fallback refusal.")
            return UNSUPPORTED_FALLBACK_MESSAGE, False

        output_lines = [
            "Based on the verified official records retrieved for your query:"
        ]
        if intro_briefing:
            output_lines.append(f"\n{intro_briefing}\n")
        else:
            output_lines.append("\n")

        output_lines.extend(valid_claims)
        output_lines.append(
            "\n*All factual statements above are traceable to the source citations displayed in the right-hand panel.*"
        )
        return "\n".join(output_lines), True

    def validate_citations_against_db(
        self, 
        db: Session, 
        citations: List[CitationItem]
    ) -> List[CitationItem]:
        """Validate that all citation document IDs and filenames exist as active indexed records in DB."""
        if not citations:
            return []

        doc_ids = [c.document_id for c in citations]
        db_docs = db.query(Document).filter(
            Document.id.in_(doc_ids),
            Document.processing_status == "INDEXED"
        ).all()
        valid_map = {d.id: d for d in db_docs}

        verified_citations = []
        for cit in citations:
            if cit.document_id in valid_map:
                real_doc = valid_map[cit.document_id]
                cit.document_name = real_doc.filename
                cit.total_pages = real_doc.page_count
                verified_citations.append(cit)
            else:
                # Also try matching by exact filename
                matching_doc = db.query(Document).filter(
                    Document.filename == cit.document_name,
                    Document.processing_status == "INDEXED"
                ).first()
                if matching_doc:
                    cit.document_id = matching_doc.id
                    cit.total_pages = matching_doc.page_count
                    verified_citations.append(cit)

        return verified_citations

validation_service = ValidationService()
