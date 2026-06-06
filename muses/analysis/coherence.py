from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Any

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "has", "have", "he", "her",
    "his", "i", "if", "in", "is", "it", "its", "me", "my", "not", "of", "or", "our", "she",
    "so", "that", "the", "their", "them", "there", "they", "this", "to", "was", "we", "were", "with",
    "you", "your",
}

ANTONYMS = {
    ("on", "off"),
    ("up", "down"),
    ("open", "closed"),
    ("true", "false"),
    ("enabled", "disabled"),
    ("present", "absent"),
    ("available", "unavailable"),
    ("success", "failure"),
    ("consistent", "inconsistent"),
    ("alive", "dead"),
}


@dataclass(slots=True)
class CoherenceFinding:
    consistent: bool
    score: float
    reasons: list[str]
    evidence: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9']+", text.lower()) if t not in STOPWORDS]


def _negated(sentence: str) -> bool:
    return bool(re.search(r"(no|not|never|without|none|n't)", sentence.lower()))


def _antonym_hit(tokens_a: set[str], tokens_b: set[str]) -> bool:
    for a, b in ANTONYMS:
        if (a in tokens_a and b in tokens_b) or (b in tokens_a and a in tokens_b):
            return True
    return False


def _score_pair(a: str, b: str) -> tuple[float, list[str]]:
    tokens_a = set(_tokens(a))
    tokens_b = set(_tokens(b))
    if not tokens_a or not tokens_b:
        return 1.0, []
    shared = tokens_a & tokens_b
    union = tokens_a | tokens_b
    overlap = len(shared) / len(union)
    reasons: list[str] = []
    if overlap > 0:
        reasons.append(f"shared_terms={sorted(shared)}")
    if _negated(a) != _negated(b) and shared:
        reasons.append("negation_mismatch")
    if _antonym_hit(tokens_a, tokens_b):
        reasons.append("antonym_conflict")
    score = max(0.0, 1.0 - (0.6 * overlap) - (0.25 if _negated(a) != _negated(b) and shared else 0.0) - (0.4 if _antonym_hit(tokens_a, tokens_b) else 0.0))
    return score, reasons


def analyze_scene(scene: str | dict[str, Any]) -> CoherenceFinding:
    if isinstance(scene, dict):
        text = str(scene.get("scene") or scene.get("text") or scene.get("description") or "")
        claims = scene.get("claims") or scene.get("sentences") or []
    else:
        text = scene
        claims = []

    if claims:
        sentences = [str(s) for s in claims if str(s).strip()]
    else:
        sentences = [s.strip() for s in re.split(r"[\n\.;]+", text) if s.strip()]

    if len(sentences) <= 1:
        return CoherenceFinding(consistent=True, score=1.0, reasons=[], evidence=sentences[:1])

    worst = 1.0
    reasons: list[str] = []
    evidence: list[str] = []
    for i, left in enumerate(sentences):
        for right in sentences[i + 1 :]:
            score, pair_reasons = _score_pair(left, right)
            if score < worst:
                worst = score
            if pair_reasons:
                reasons.extend(pair_reasons)
                evidence.extend([left, right])

    inconsistent = worst < 0.7 or any(r in {"negation_mismatch", "antonym_conflict"} for r in reasons)
    return CoherenceFinding(
        consistent=not inconsistent,
        score=round(worst, 3),
        reasons=sorted(set(reasons)),
        evidence=list(dict.fromkeys(evidence))[:4],
    )


def analyze_session(session: dict[str, Any]) -> CoherenceFinding:
    turns = session.get("turns") or session.get("messages") or []
    lines = []
    for turn in turns:
        if isinstance(turn, dict):
            lines.append(str(turn.get("content") or turn.get("text") or ""))
        else:
            lines.append(str(turn))
    return analyze_scene({"sentences": lines})
