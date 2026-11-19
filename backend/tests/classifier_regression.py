"""Live check of the SQL-vs-document classifier against known questions.

Calls the real LLM, so it needs LLM_API_KEY in backend/.env and network access. It is
deliberately not named test_*.py: pytest (and CI, which has no API key) does not collect it.

Run from the backend folder:
    python -m tests.classifier_regression

Prints one line per question and exits with status 1 if any question is routed differently
from the expected route.
"""
import sys

from app.rag.classifier import classify_question

CASES = [
    # Policy, procedure and dosage questions answered from documents.
    ("What is the standard dose of Atorvastatin?", "document"),
    ("What is the correct hand hygiene technique?", "document"),
    ("What is the process for submitting a claim?", "document"),
    ("What does fault code E-12 mean?", "document"),
    ("What is the maximum bill amount for a general ward patient?", "document"),
    ("How to prevent blood infection?", "document"),
    # Not answerable from the claims or maintenance_tickets tables.
    ("How many leaves do I have?", "document"),
    ("What's the weather today?", "document"),
    # Questions about the actual records in claims or maintenance_tickets.
    ("How many billing claims are currently pending?", "analytical"),
    ("How many billing claims were escalated?", "analytical"),
    ("Which equipment category has the most open maintenance tickets?", "analytical"),
    ("What is the total claimed amount for cardiology department claims?", "analytical"),
    ("How many maintenance tickets are open for infusion equipment?", "analytical"),
    ("Compare the number of escalated claims to the number of escalated maintenance tickets.", "analytical"),
    ("Tell me about the claims.", "analytical"),
    ("Tell me about the maintenance tickets.", "analytical"),
    ("How many claims are there for the orthopedics department?", "analytical"),
    ("What is the maximum amount billed till date", "analytical"),
]


def main() -> int:
    mismatches = 0
    for question, expected in CASES:
        actual = classify_question(question)
        ok = actual == expected
        mismatches += not ok
        print(f"{'OK ' if ok else 'BAD'} expected={expected:<10} actual={actual:<10} {question}")
    print(f"{len(CASES) - mismatches}/{len(CASES)} routed as expected")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
