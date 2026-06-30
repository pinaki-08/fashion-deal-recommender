from recommender import (
    SemanticMatcher,
    detect_discount,
    parse_price,
    rank_by_deal,
    rank_by_similarity,
)


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


def test_parse_price_variants():
    assert parse_price("$1,299.00") == 1299.0
    assert parse_price("Rs. 999") == 999.0
    assert parse_price("89.99") == 89.99
    assert parse_price("N/A") is None
    assert parse_price(None) is None
    assert parse_price(50) == 50.0


def test_rank_by_deal_prefers_cheaper_when_similar():
    query = "running shoes"
    items = [
        {"name": "running shoes", "price": "$100"},
        {"name": "running shoes", "price": "$60"},
    ]
    ranked = rank_by_deal(query, items, source_price="$120")

    # Equal name similarity, so the cheaper item should win on deal_score.
    assert ranked[0]["price"] == "$60"
    assert ranked[0]["savings"] == 60.0
    assert all("deal_score" in item for item in ranked)
    scores = [item["deal_score"] for item in ranked]
    assert scores == sorted(scores, reverse=True)


def test_rank_by_deal_cheaper_only_filters_pricier_items():
    items = [
        {"name": "jacket", "price": "$200"},
        {"name": "jacket", "price": "$50"},
    ]
    ranked = rank_by_deal("jacket", items, source_price="$100", cheaper_only=True)

    assert len(ranked) == 1
    assert ranked[0]["price"] == "$50"


def test_rank_by_deal_keeps_unknown_prices():
    items = [{"name": "jacket", "price": "N/A"}]
    ranked = rank_by_deal("jacket", items, source_price="$100", cheaper_only=True)

    assert len(ranked) == 1
    assert ranked[0]["parsed_price"] is None


def test_detect_discount_on_sale():
    deal = detect_discount("$80", "$100")
    assert deal["on_sale"] is True
    assert deal["discount"] == 20.0
    assert deal["discount_pct"] == 20.0


def test_detect_discount_not_on_sale():
    # Current price higher than "original" is not a discount.
    assert detect_discount("$100", "$80")["on_sale"] is False
    # Missing original price is not a discount.
    assert detect_discount("$50", None)["on_sale"] is False
