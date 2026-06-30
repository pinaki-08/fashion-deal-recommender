# --- Semantic similarity recommender ---
#
# Ranks candidate products by how semantically similar their text
# (name + description) is to a query product.
#
# Primary backend: sentence-transformers (all-MiniLM-L6-v2) which produces
# real sentence embeddings and cosine similarity. If that library/model is
# not available (e.g. offline CI), it transparently falls back to a
# deterministic bag-of-words cosine so the feature always works.

import math
import re

_STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "with", "of", "in", "on", "to",
    "size", "color", "colour", "new", "men", "women", "unisex",
}


class SemanticMatcher:
    """Lazily-loaded semantic similarity engine."""

    _model = None
    _load_failed = False

    @classmethod
    def _get_model(cls):
        if cls._model is None and not cls._load_failed:
            try:
                from sentence_transformers import SentenceTransformer

                cls._model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                # No model / offline -> use deterministic fallback
                cls._load_failed = True
        return cls._model

    @classmethod
    def similarity(cls, text_a, text_b):
        """Return a similarity score in [0, 1] between two strings."""
        text_a = (text_a or "").strip()
        text_b = (text_b or "").strip()
        if not text_a or not text_b:
            return 0.0

        model = cls._get_model()
        if model is not None:
            from sentence_transformers import util

            emb = model.encode([text_a, text_b], convert_to_tensor=True)
            score = float(util.cos_sim(emb[0], emb[1])[0][0])
            # Clamp to [0, 1]
            return max(0.0, min(1.0, score))

        return _bow_cosine(text_a, text_b)


def _tokens(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS]


def _bow_cosine(text_a, text_b):
    """Deterministic bag-of-words cosine similarity fallback."""
    tokens_a = _tokens(text_a)
    tokens_b = _tokens(text_b)
    if not tokens_a or not tokens_b:
        return 0.0

    vocab = set(tokens_a) | set(tokens_b)
    vec_a = {w: tokens_a.count(w) for w in vocab}
    vec_b = {w: tokens_b.count(w) for w in vocab}

    dot = sum(vec_a[w] * vec_b[w] for w in vocab)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_by_similarity(query, items, text_key="name", top_k=None):
    """
    Rank ``items`` (list of dicts) by semantic similarity of ``item[text_key]``
    to ``query``. Adds a ``similarity_score`` field (rounded) to each item and
    returns the list sorted from most to least similar.
    """
    scored = []
    for item in items:
        score = SemanticMatcher.similarity(query, item.get(text_key, ""))
        enriched = dict(item)
        enriched["similarity_score"] = round(score, 4)
        scored.append(enriched)

    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    if top_k is not None:
        scored = scored[:top_k]
    return scored


def parse_price(value):
    """
    Parse a price from a string/number into a float, or ``None`` if no numeric
    value can be found. Handles currency symbols and thousands separators,
    e.g. ``"$1,299.00"`` -> ``1299.0``, ``"Rs. 999"`` -> ``999.0``.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    match = re.search(r"\d[\d,]*(?:\.\d+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None


def rank_by_deal(
    query,
    items,
    source_price=None,
    text_key="name",
    price_key="price",
    top_k=None,
    similarity_weight=0.7,
    cheaper_only=False,
):
    """
    Rank ``items`` as *deals*: a blend of semantic similarity to ``query`` and
    how much cheaper each item is than ``source_price``.

    Each returned item is annotated with:
      - ``similarity_score``: text similarity in [0, 1]
      - ``parsed_price``: numeric price (or ``None`` if unknown)
      - ``savings``: source_price - parsed_price (or ``None``)
      - ``savings_pct``: percentage saved vs. source (or ``None``)
      - ``deal_score``: combined ranking score

    ``similarity_weight`` balances similarity vs. savings (0..1). When
    ``cheaper_only`` is True, items priced at or above the source (with a known
    price) are dropped. Items with unknown prices are always kept.
    """
    src = parse_price(source_price)
    sim_w = max(0.0, min(1.0, similarity_weight))

    scored = []
    for item in items:
        similarity = SemanticMatcher.similarity(query, item.get(text_key, ""))
        price = parse_price(item.get(price_key))

        savings = None
        savings_pct = None
        savings_ratio = 0.0
        if src is not None and src > 0 and price is not None:
            savings = round(src - price, 2)
            savings_ratio = max(0.0, (src - price) / src)
            savings_pct = round(savings_ratio * 100, 2)

        if cheaper_only and src is not None and price is not None and price >= src:
            continue

        deal_score = sim_w * similarity + (1 - sim_w) * savings_ratio

        enriched = dict(item)
        enriched["similarity_score"] = round(similarity, 4)
        enriched["parsed_price"] = price
        enriched["savings"] = savings
        enriched["savings_pct"] = savings_pct
        enriched["deal_score"] = round(deal_score, 4)
        scored.append(enriched)

    scored.sort(key=lambda x: x["deal_score"], reverse=True)
    if top_k is not None:
        scored = scored[:top_k]
    return scored


def detect_discount(current_price, original_price):
    """
    Compare a current price against an original (struck-through) price and
    report the discount.

    Returns a dict with:
      - ``current_price``/``original_price``: parsed floats (or ``None``)
      - ``on_sale``: True when original > current > 0
      - ``discount``: absolute amount saved (or ``None``)
      - ``discount_pct``: percentage off the original (or ``None``)
    """
    cur = parse_price(current_price)
    orig = parse_price(original_price)

    result = {
        "current_price": cur,
        "original_price": orig,
        "on_sale": False,
        "discount": None,
        "discount_pct": None,
    }
    if cur is not None and orig is not None and orig > cur > 0:
        result["on_sale"] = True
        result["discount"] = round(orig - cur, 2)
        result["discount_pct"] = round((orig - cur) / orig * 100, 2)
    return result
