from __future__ import annotations

from muses.api.server import app


def test_analysis_endpoints_expose_expected_contracts():
    health = app.handle("GET", "/v1/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    scene = app.handle("POST", "/v1/analyze/consistency_scene", {"sentences": ["The light is on.", "The light is off."]})
    assert scene.status_code == 200
    body = scene.json()
    assert body["ok"] is True
    assert body["consistent"] is False

    summary = app.handle("POST", "/v1/analyze/summary", {"documents": [{"id": "x", "text": "First sentence. Second sentence."}]})
    assert summary.status_code == 200
    assert summary.json()["summary"]

    links = app.handle("POST", "/v1/analyze/federated_links", {"query": {"embedding": [1, 0]}, "candidates": [{"id": "c", "embedding": [1, 0]}]})
    assert links.status_code == 200
    assert links.json()["links"]
