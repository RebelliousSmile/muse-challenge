from __future__ import annotations

from dataclasses import dataclass, asdict
from math import sqrt
from typing import Any, Sequence


@dataclass(slots=True)
class FederatedLink:
    source_id: str
    target_id: str
    score: float
    label: str | None = None

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


def find_links(query: dict[str, Any], candidates: list[dict[str, Any]], min_score: float = 0.75) -> list[FederatedLink]:
    q_emb = query.get("embedding") or []
    q_id = str(query.get("id", "query"))
    links: list[FederatedLink] = []
    for candidate in candidates:
        c_emb = candidate.get("embedding") or []
        score = _cosine(q_emb, c_emb)
        if score >= min_score:
            links.append(
                FederatedLink(
                    source_id=q_id,
                    target_id=str(candidate.get("id", "candidate")),
                    score=round(float(score), 3),
                    label=candidate.get("label"),
                )
            )
    links.sort(key=lambda item: item.score, reverse=True)
    return links
