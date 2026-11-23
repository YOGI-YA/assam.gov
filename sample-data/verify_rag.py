import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service

def test_rag():
    db = SessionLocal()
    try:
        # Test 1: Supported query
        q1 = "What is the maximum gratuity limit under Assam Pension Rules?"
        cits1 = retrieval_service.retrieve_relevant_chunks(db, query=q1, top_k=3)
        ans1, grounded1 = llm_service.generate_grounded_answer(q1, cits1)
        print(f"--- TEST 1: Supported Query ---")
        print(f"Q: {q1}")
        print(f"Citations found: {len(cits1)}")
        for c in cits1:
            print(f"  [{c.citation_id}] {c.document_name} P.{c.page_number} (score: {c.similarity_score})")
        print(f"Grounded: {grounded1}")
        print(f"Answer snippet: {ans1[:180]}...\n")

        # Test 2: Another supported query with specific rule
        q2 = "Who is the apex state nodal agency for satellite remote sensing and GIS mapping in Assam?"
        cits2 = retrieval_service.retrieve_relevant_chunks(db, query=q2, top_k=3)
        ans2, grounded2 = llm_service.generate_grounded_answer(q2, cits2)
        print(f"--- TEST 2: Supported Query (ASSAC) ---")
        print(f"Q: {q2}")
        print(f"Citations found: {len(cits2)}")
        for c in cits2:
            print(f"  [{c.citation_id}] {c.document_name} P.{c.page_number} (score: {c.similarity_score})")
        print(f"Answer snippet: {ans2[:180]}...\n")

        # Test 3: Unsupported query
        q3 = "What is the procedure for registering a nuclear power submarine in Assam?"
        cits3 = retrieval_service.retrieve_relevant_chunks(db, query=q3, top_k=3, threshold=0.35)
        ans3, grounded3 = llm_service.generate_grounded_answer(q3, cits3)
        print(f"--- TEST 3: Unsupported Query ---")
        print(f"Q: {q3}")
        print(f"Citations count: {len(cits3)}")
        print(f"Grounded: {grounded3}")
        print(f"Answer: {ans3}\n")

    finally:
        db.close()

if __name__ == "__main__":
    test_rag()
