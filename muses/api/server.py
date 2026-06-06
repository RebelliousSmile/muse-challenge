from __future__ import annotations

from dataclasses import dataclass

from muses.analysis.coherence import analyze_scene, analyze_session
from muses.analysis.federated_links import find_links
from muses.analysis.summary import summarize


@dataclass(slots=True)
class Response:
    status_code: int
    body: dict

    def json(self) -> dict:
        return self.body


class AnalysisApp:
    def handle(self, method: str, path: str, payload: dict | None = None) -> Response:
        payload = payload or {}
        if method == "GET" and path == "/v1/health":
            return Response(200, {"status": "ok"})
        if method == "POST" and path == "/v1/analyze/consistency_scene":
            result = analyze_scene(payload)
            return Response(200, {"ok": True, **result.to_dict()})
        if method == "POST" and path == "/v1/analyze/consistency_session":
            result = analyze_session(payload)
            return Response(200, {"ok": True, **result.to_dict()})
        if method == "POST" and path == "/v1/analyze/summary":
            result = summarize(payload)
            return Response(200, {"ok": True, **result.to_dict()})
        if method == "POST" and path == "/v1/analyze/federated_links":
            links = find_links(payload.get("query", {}), payload.get("candidates", []), min_score=payload.get("min_score", 0.75))
            return Response(200, {"ok": True, "links": [link.to_dict() for link in links]})
        return Response(404, {"detail": "not_found"})


def create_app() -> AnalysisApp:
    return AnalysisApp()


app = create_app()
