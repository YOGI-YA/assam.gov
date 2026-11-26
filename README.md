# assam.gov — Government Knowledge Assistant (NESFIC 2026 MVP)

**Challenge ID:** NESFIC-D-36 | **Stream 1:** Governance & Administrative Intelligence  
**Administrative Context:** Assam Administrative Staff College (AASC), Department of Science & Technology (DST), and Assam State Space Application Centre (ASSAC).  
**Core Product Philosophy:** *Every AI-generated answer must be traceable to its authentic source document, exact page number, and supporting passage.*

---

## 1. Executive Summary

assam.gov is a secure, source-grounded document intelligence platform developed as an MVP for government officers. In administrative departments, officers must review extensive circulars, manuals, notifications, and office orders. GovSaarthi allows authorized personnel to query indexed government documents, receive factually grounded answers with verified citations, inspect original PDF pages side-by-side, generate standard Assam Government administrative drafts (Office Notes, Formal Letters, Office Orders), and maintain immutable audit trails.

> **Demonstration Environment Disclaimer:**  
> This application is a technical demonstration MVP developed for the NESFIC 2026 challenge. It clearly identifies itself as a demonstration prototype and does not imply that it is an officially deployed Assam Government production system.

---

## 2. Core Functional Modules

### Module 1: Ask gov.guide (Flagship 3-Column Interface)
- **Left Column:** Conversation history, past queries, and document scope filter.
- **Center Column:** Interactive chat stream with grounded answers, citation pills, copy button, and grounded badges.
- **Right Column:** Source Document Preview Panel. Clicking any citation immediately loads the original PDF and jumps directly to the cited page, displaying the supporting excerpt side-by-side.
- **Anti-Hallucination Guardrail:** If an answer cannot be found in the indexed documents, GovSaarthi strictly refuses:  
  *"I could not find sufficient supporting information in the available documents. Please consult the relevant department or authorised source."*

### Module 2: Documents Management
- Upload PDF documents (up to 25MB).
- Page-by-page text extraction using **PyMuPDF**.
- Preservation of original page-level numbering.
- Semantic chunking with overlap and vector embeddings.
- Dual storage engine: **PostgreSQL with pgvector** with automatic seamless fallback to local SQLite vector search.
- Document listing, category filter, search, inspection, and deletion.

### Module 3: AI Drafting Studio
- Split-screen drafting interface:
  - **Left:** Select document format (Office Note, Formal Letter, Office Order, Executive Summary), target authority, subject, reference documents, and administrative instructions.
  - **Right:** Generated draft formatted to Assam Government Secretariat conventions, editable before saving, with copy and download actions.
  - **Watermark:** Every draft is prominently marked: `DRAFT ONLY — Requires human review, verification and authorized signature before issuance`.

### Module 4: Audit & Traceability Logs
- Records all critical user actions: `LOGIN`, `DOCUMENT_UPLOAD`, `DOCUMENT_DELETE`, `CHAT_QUERY`, `CONTEXT_RETRIEVAL`, `RESPONSE_GENERATED`, `GENERATE_DRAFT`, and `SUMMARIZE`.
- Captures timestamps, user roles, document IDs, query snippets, and retrieval scores.

### Landing Dashboard
- Displays real-time database counts: total documents, indexed documents, queries answered, drafts created, and recent questions.

---

## 3. Project Architecture

```
assam.gov/
│
├── frontend/                     # Next.js 15 (TypeScript, Tailwind CSS, Lucide React)
│   ├── app/                      # App Router pages (/chat, /documents, /drafting, /audit)
│   ├── components/               # UI & layout components
│   │   ├── layout/               # Navbar, Sidebar, AppLayout
│   │   ├── chat/                 # AskGovSaarthi, SourcePreviewPanel
│   │   ├── documents/            # DocumentList, DocumentUploadModal
│   │   ├── drafting/             # DraftingStudio
│   │   └── dashboard/            # DashboardOverview
│   ├── lib/                      # API client
│   └── types/                    # TypeScript interfaces
│
├── backend/                      # Python FastAPI application
│   ├── app/
│   │   ├── api/                  # Endpoints (auth, documents, chat, drafting, audit, dashboard)
│   │   ├── core/                 # Config, database engine, security (PBKDF2/JWT)
│   │   ├── models/               # SQLAlchemy models (User, Document, DocumentChunk, AuditLog)
│   │   ├── schemas/              # Pydantic schemas
│   │   └── services/
│   │       ├── document_service.py   # PyMuPDF extraction & chunking
│   │       ├── embedding_service.py  # 384-dim dense vector embeddings
│   │       ├── retrieval_service.py  # pgvector & hybrid cosine similarity retrieval
│   │       ├── llm_service.py        # Grounded generation & drafting
│   │       └── audit_service.py      # Traceability logger
│   └── main.py                   # FastAPI app entry point
│
├── sample-data/                  # Authentic Assam Government demonstration dataset
│   ├── generate_sample_pdfs.py   # PDF synthesis script using PyMuPDF
│   ├── seed_database.py          # Indexes sample documents into DB
│   ├── verify_rag.py             # RAG & citation verification script
│   └── verify_e2e.py             # 13 MVP Acceptance Criteria test suite
│
├── docker-compose.yml            # PostgreSQL with pgvector container
├── .env.example                  # Environment variable template
└── README.md
```

---

## 4. Getting Started

### Prerequisites
- **Python:** 3.10 to 3.14
- **Node.js:** v18+ (tested on Node v24)
- **Database:** PostgreSQL (with `pgvector`) or zero-config local SQLite (automatically handled)

### Step 1: Clone and Configure Environment
```bash
git clone <repo-url>
cd assam.gov
copy .env.example .env
```

### Step 2: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Seed Demonstration Government Data
```bash
cd ..
python sample-data/generate_sample_pdfs.py
python sample-data/seed_database.py
```
This indexes 4 sample Assam Government documents:
1. `Assam_Secretariat_Manual_of_Office_Procedure.pdf` (3 pages)
2. `DST_ASSAC_Remote_Sensing_Notification.pdf` (2 pages)
3. `AASC_State_Training_Policy_Guidelines.pdf` (2 pages)
4. `Assam_Pension_Rules_Circular_No_142.pdf` (1 page)

### Step 4: Run the Backend
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API docs available at: `http://127.0.0.1:8000/docs`

### Step 5: Run the Frontend
```bash
cd ../frontend
npm install
npm run dev
```
Open your browser at: `http://localhost:3000`

---

## 5. Demonstration Test Walkthrough

### 1. Source-Grounded Question Answering
Navigate to **Ask GovSaarthi** (`/chat`):
- **Query 1:** *"What is the maximum gratuity limit under Assam Pension Rules?"*  
  **Expected Result:** Answers citing ceiling of Rs. 20,00,000 from `Assam_Pension_Rules_Circular_No_142.pdf` Page 1.
- **Query 2:** *"Who is the apex state nodal agency for satellite remote sensing and GIS mapping in Assam?"*  
  **Expected Result:** Answers citing Assam State Space Application Centre (ASSAC) from `DST_ASSAC_Remote_Sensing_Notification.pdf` Page 1.

### 2. Answer-to-Source Verification
- Click on any citation badge in the AI answer (e.g., `[CIT-1] Assam_Pension_Rules_Circular_No_142.pdf P.1`).
- The **Source Document Preview Panel** on the right opens the exact PDF and jumps directly to that page, showing the excerpt above the embedded PDF viewer.

### 3. Anti-Hallucination Refusal
- **Query:** *"What is the procedure for registering a nuclear power submarine in Assam?"*  
  **Expected Result:**  
  *"I could not find sufficient supporting information in the available documents. Please consult the relevant department or authorised source."*

### 4. Drafting Studio
Navigate to **Drafting Studio** (`/drafting`):
- Click **Office Note** template.
- Subject: *"Sanction of contingent expenditure for IT infrastructure upgrading at AASC"*.
- Click **Generate Official Draft**.
- Verify generated Green Note Sheet format, citations, and the `DRAFT ONLY` watermark.

### 5. Audit Log Inspection
Navigate to **Audit Logs** (`/audit`):
- Inspect the immutable record of all queries, uploads, and AI responses.

---

## 6. Automated Verification Suite

Run the end-to-end acceptance test suite to verify all 13 challenge criteria:
```bash
python sample-data/verify_e2e.py
```

Output:
```
==================================================================
GOVSAARTHI — MVP ACCEPTANCE CRITERIA AUTOMATED VERIFICATION SUITE
==================================================================
✓ 1. Authorised user can log in: PASS
✓ 2, 3, 4. Document management & indexing: PASS (4 documents verified)
✓ 5, 6, 7, 8. Grounded RAG & Citations: PASS (Top citation: Assam_Pension_Rules_Circular_No_142.pdf Page 1)
✓ 9. Original PDF streaming & preview endpoint: PASS
✓ 10. Anti-hallucination guardrail (unsupported query refusal): PASS
✓ 11. Executive document summary generation: PASS
✓ 12. Office Note / Order draft generation: PASS
✓ 13. Activity & Audit tracking: PASS (16+ audit logs on record)
==================================================================
ALL 13 MVP ACCEPTANCE CRITERIA VERIFIED AND FULLY PASSING!
==================================================================
```

---

## 7. Default Demonstration Accounts

| Role | Email | Password | Department |
|---|---|---|---|
| **Admin** | `admin@aasc.assam.gov.in` | `AssamGov@2026` | Assam Administrative Staff College |
| **Officer** | `officer@dst.assam.gov.in` | `GovSaarthi@2026` | Dept. of Science & Technology / ASSAC |

---

## 8. License & Challenge Attribution
Developed for **NESFIC 2026 Challenge NESFIC-D-36**.  
Designed with white/light grey administrative surfaces and navy blue primary colors according to government UI standards.
