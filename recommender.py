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
