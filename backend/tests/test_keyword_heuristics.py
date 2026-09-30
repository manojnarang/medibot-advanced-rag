from app.rbac.keyword_heuristics import find_restricted_collection_mention


def test_restricted_collection_mention_word_boundary():
    assert find_restricted_collection_mention("show me insurance billing codes", ["general", "nursing"]) == "billing"
    assert find_restricted_collection_mention("what is the leave policy?", ["general", "nursing"]) is None
