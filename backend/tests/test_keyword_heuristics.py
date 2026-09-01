from app.rbac.keyword_heuristics import (
    find_restricted_collection_mention,
    looks_analytical,
)


def test_looks_analytical_matches_real_keywords():
    assert looks_analytical("How many claims were escalated last month?")
    assert looks_analytical("What is the average claim amount?")
    assert looks_analytical("Give me a breakdown of open tickets by category.")


def test_looks_analytical_does_not_false_positive_on_substrings():
    """Regression test: short keywords like 'count'/'sum'/'total' must be
    matched as whole words, not as substrings of unrelated words."""
    assert not looks_analytical("Can you summarize the staff leave policy?")
    assert not looks_analytical("Is there a discount on the annual health checkup?")
    assert not looks_analytical("What does the accounting department handle?")
    assert not looks_analytical("The ward was totally reorganised last year.")


def test_looks_analytical_requires_domain_word_not_just_a_quantifier():
    """'How many X' alone isn't enough - X has to plausibly be about the
    claims/maintenance_tickets tables SQL RAG actually covers. A generic
    quantifier question about something else (e.g. leave balance) should
    fall through to hybrid RAG instead of being treated as analytical."""
    assert not looks_analytical("How many leaves do I have?")
    assert not looks_analytical("How many sick days are allowed per year?")
    assert looks_analytical("How many claims were escalated last month?")
    assert looks_analytical("How many maintenance tickets are open?")


def test_restricted_collection_mention_word_boundary():
    assert find_restricted_collection_mention("show me insurance billing codes", ["general", "nursing"]) == "billing"
    assert find_restricted_collection_mention("what is the leave policy?", ["general", "nursing"]) is None
