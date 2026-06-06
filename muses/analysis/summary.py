from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Any

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have", "i", "in", "is",
    "it", "its", "of", "on", "or", "that", "the", "this", "to", "was", "we", "with", "you",
}


@dataclass(slots=True)
class SummaryResult:
    summary: str
    trace: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|[\n\r]+", text) if s.strip()]


def _keywords(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9']+", text.lower()) if t not in STOPWORDS}


def summarize(payload: dict[str, Any]) -> SummaryResult:
    items = payload.get("documents") or payload.get("chunks") or payload.get("texts") or []
    source_ids: list[str] = []
    sentences: list[str] = []
    for idx, item in enumerate(items):
        if isinstance(item, dict):
            source_ids.append(str(item.get("id", idx)))
            content = str(item.get("text") or item.get("content") or "")
        else:
            source_ids.append(str(idx))
            content = str(item)
        sentences.extend(_sentences(content))

    if not sentences:
        return SummaryResult(summary="", trace={"source_ids": source_ids, "selected_sentences": []})

    if len(sentences) == 1:
        return SummaryResult(summary=sentences[0], trace={"source_ids": source_ids, "selected_sentences": [sentences[0]]})

    topic_counts: dict[str, int] = {}
    for sentence in sentences:
        for token in _keywords(sentence):
            topic_counts[token] = topic_counts.get(token, 0) + 1

    ranked = sorted(
        sentences,
        key=lambda s: (sum(topic_counts.get(tok, 0) for tok in _keywords(s)), len(s)),
        reverse=True,
    )
    selected = ranked[:2]
    summary = " ".join(selected)
    return SummaryResult(summary=summary, trace={"source_ids": source_ids, "selected_sentences": selected})
