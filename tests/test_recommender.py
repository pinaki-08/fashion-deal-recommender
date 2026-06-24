from recommender import SemanticMatcher, rank_by_similarity


def test_similarity_self_is_high():
    score = SemanticMatcher.similarity("blue denim jacket", "blue denim jacket")
    assert score > 0.99


def test_similarity_related_beats_unrelated():
    query = "blue denim jacket"
    related = SemanticMatcher.similarity(query, "denim jacket blue")
    unrelated = SemanticMatcher.similarity(query, "red leather handbag")
    assert related > unrelated


def test_rank_by_similarity_orders_and_annotates():
    query = "running shoes"
    items = [
        {"name": "leather wallet"},
        {"name": "mens running shoes"},
        {"name": "sports running sneakers shoes"},
    ]
    ranked = rank_by_similarity(query, items, text_key="name")

    assert all("similarity_score" in item for item in ranked)
    # Most similar should come first
    assert "running" in ranked[0]["name"]
    # Sorted descending
    scores = [item["similarity_score"] for item in ranked]
    assert scores == sorted(scores, reverse=True)


def test_rank_by_similarity_top_k():
    items = [{"name": f"item {i}"} for i in range(5)]
    ranked = rank_by_similarity("item", items, text_key="name", top_k=2)
    assert len(ranked) == 2


def test_empty_strings_score_zero():
    assert SemanticMatcher.similarity("", "anything") == 0.0
