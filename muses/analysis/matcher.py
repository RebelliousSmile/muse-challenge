from __future__ import annotations

from dataclasses import dataclass, asdict
from math import sqrt
from typing import Any, Sequence


@dataclass(slots=True)
class MatchLink:
    source_id: str
    target_id: str
    score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def match_embeddings(source: dict[str, Any], targets: list[dict[str, Any]], min_score: float = 0.65) -> list[MatchLink]:
    source_id = str(source.get("id", "source"))
    source_emb = source.get("embedding") or []
    links: list[MatchLink] = []
    for target in targets:
        target_emb = target.get("embedding") or []
        score = _cosine(source_emb, target_emb)
        if score >= min_score:
            links.append(
                MatchLink(
                    source_id=source_id,
                    target_id=str(target.get("id", "target")),
                    score=round(float(score), 3),
                    reason="embedding_similarity",
                )
            )
    links.sort(key=lambda item: item.score, reverse=True)
    return links
