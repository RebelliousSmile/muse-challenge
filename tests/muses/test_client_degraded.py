from __future__ import annotations

from muses.analysis.coherence import analyze_scene, analyze_session
from muses.analysis.federated_links import find_links
from muses.analysis.summary import summarize
from muses.client import MusesClient, TransportResponse


class AlwaysTimeoutTransport:
    def request(self, method, path, json=None):
        raise TimeoutError("timed out")


class ServiceUnavailableTransport:
    def request(self, method, path, json=None):
        return TransportResponse(status_code=503, json_data={"detail": "unavailable"})


def test_client_grays_out_when_timeout_occurs():
    client = MusesClient("http://muses.local", transport=AlwaysTimeoutTransport())
    result = client.health()
    assert not result.ok
    assert result.data is None
    assert result.status.degraded is True
    assert result.status.available is False
    assert result.status.ui_state == "grayed"
    assert result.status.reason == "service_unavailable"
    client.close()


def test_client_grays_out_when_backend_returns_error():
    client = MusesClient("http://muses.local", transport=ServiceUnavailableTransport())
    result = client.analyze_consistency_scene(scene={"scene": "The light is on. The light is off."})
    assert not result.ok
    assert result.data is None
    assert result.status.degraded is True
    assert result.status.ui_state == "grayed"
    assert result.status.reason == "http_503"
    client.close()


def test_consistency_scene_detects_known_contradiction_and_avoids_false_positive_on_coherent_case():
    incoherent = analyze_scene({"sentences": ["The light is on.", "The light is off."]})
    coherent = analyze_scene({"sentences": ["The light is on.", "The lamp remains on."]})
    assert incoherent.consistent is False
    assert incoherent.reasons
    assert coherent.consistent is True
    assert coherent.score >= 0.7


def test_consistency_session_flags_conflict_across_turns():
    result = analyze_session({"turns": [
        {"role": "assistant", "content": "I will ship the patch today."},
        {"role": "assistant", "content": "I will not ship the patch today."},
    ]})
    assert result.consistent is False
    assert result.evidence


def test_summary_pipeline_is_non_empty_and_traceable():
    result = summarize({"documents": [
        {"id": "a", "text": "The client must not invent answers. It should surface unavailability."},
        {"id": "b", "text": "A degraded UI should gray out controls and report the backend state."},
    ]})
    assert result.summary
    assert result.trace["source_ids"] == ["a", "b"]
    assert result.trace["selected_sentences"]


def test_federated_links_returns_relevant_candidates_and_can_be_empty():
    query = {"id": "q1", "embedding": [1.0, 0.0, 0.0]}
    candidates = [
        {"id": "good", "embedding": [0.98, 0.02, 0.0], "label": "near"},
        {"id": "bad", "embedding": [0.0, 1.0, 0.0], "label": "far"},
    ]
    links = find_links(query, candidates, min_score=0.8)
    assert [l.target_id for l in links] == ["good"]
    empty = find_links(query, [{"id": "none", "embedding": [0.0, 1.0, 0.0]}], min_score=0.9)
    assert empty == []
