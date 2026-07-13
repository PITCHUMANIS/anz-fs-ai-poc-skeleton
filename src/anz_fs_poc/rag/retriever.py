from __future__ import annotations

import re

from anz_fs_poc.models import Citation
from anz_fs_poc.rag.corpus import Chunk

# Without stopword filtering the lexical scorer matches on words like "the"/"for",
# so unrelated queries score above threshold and the §6.3 "I don't know" path
# never triggers. Dropping function words makes retrieval reflect content overlap.
_STOPWORDS = {
    "the", "and", "for", "are", "you", "your", "our", "who", "what", "how",
    "why", "when", "where", "which", "this", "that", "with", "from", "into",
    "have", "has", "had", "was", "were", "will", "would", "should", "could",
    "can", "does", "did", "not", "but", "all", "any", "its", "his", "her",
    "their", "them", "they", "then", "than", "about", "please", "explain",
    "include", "including", "need", "want", "get", "got", "use", "using",
    "there", "here", "over", "under", "such", "may", "must", "per",
}


def _tokens(text: str) -> set[str]:
    return {
        t
        for t in re.findall(r"[a-z0-9]+", text.lower())
        if len(t) > 2 and t not in _STOPWORDS
    }


def retrieve(query: str, chunks: list[Chunk], *, top_k: int = 3, min_score: float = 0.15) -> list[Citation]:
    """Simple lexical retriever for the offline PoC — swap for vector search later."""
    q = _tokens(query)
    if not q:
        return []

    scored: list[tuple[float, Chunk]] = []
    for chunk in chunks:
        c = _tokens(chunk.text) | _tokens(chunk.section) | {chunk.doc_id.lower()}
        overlap = len(q & c)
        score = overlap / max(len(q), 1)
        # Light boosts for known intents
        if "fee" in q and ("fee" in c or "charges" in c or "annual" in c):
            score += 0.2
        if "complaint" in q and ("complaint" in c or "escalation" in c):
            score += 0.2
        if "offset" in q and "offset" in c:
            score += 0.25
        if score >= min_score:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    citations: list[Citation] = []
    for score, chunk in scored[:top_k]:
        preview = " ".join(chunk.text.split())[:180]
        citations.append(
            Citation(doc_id=chunk.doc_id, section=chunk.section, preview=preview + ("…" if len(preview) == 180 else ""), score=round(score, 3))
        )
    return citations
