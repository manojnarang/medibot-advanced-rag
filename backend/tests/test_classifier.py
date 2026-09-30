from unittest.mock import patch

from app.rag.classifier import classify_question


@patch("app.rag.classifier.generate")
def test_classify_question_parses_analytical(mock_generate):
    mock_generate.return_value = "analytical"
    assert classify_question("How many claims were escalated?") == "analytical"


@patch("app.rag.classifier.generate")
def test_classify_question_parses_document(mock_generate):
    mock_generate.return_value = "document"
    assert classify_question("What is the infection control procedure?") == "document"


@patch("app.rag.classifier.generate")
def test_classify_question_defaults_to_document_on_unexpected_output(mock_generate):
    mock_generate.return_value = "unsure"
    assert classify_question("Some ambiguous question") == "document"


@patch("app.rag.classifier.generate")
def test_classify_question_defaults_to_document_on_llm_failure(mock_generate):
    """Safe fallback: if the classification call itself fails (LLM provider
    unavailable), route to hybrid RAG rather than raising - a failed hybrid
    RAG answer degrades gracefully, unlike running SQL RAG on a
    misclassified question."""
    mock_generate.side_effect = Exception("provider unavailable")
    assert classify_question("How many claims were escalated?") == "document"
