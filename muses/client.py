from __future__ import annotations

from dataclasses import dataclass
from json import dumps, loads
from typing import Any, Protocol, runtime_checkable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(slots=True)
class ClientStatus:
    available: bool
    degraded: bool
    ui_state: str
    reason: str | None = None
    error: str | None = None


@dataclass(slots=True)
class ClientResult:
    ok: bool
    data: Any | None
    status: ClientStatus


@dataclass(slots=True)
class TransportResponse:
    status_code: int
    json_data: Any

    def json(self) -> Any:
        return self.json_data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


@runtime_checkable
class Transport(Protocol):
    def request(self, method: str, path: str, json: dict[str, Any] | None = None) -> TransportResponse: ...


class _UrllibTransport:
    def __init__(self, base_url: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method: str, path: str, json: dict[str, Any] | None = None) -> TransportResponse:
        url = f"{self.base_url}{path}"
        data = None if json is None else dumps(json).encode("utf-8")
        headers = {"Content-Type": "application/json"} if json is not None else {}
        req = Request(url, data=data, headers=headers, method=method)
        with urlopen(req, timeout=self.timeout) as resp:
            payload = loads(resp.read().decode("utf-8") or "null")
            return TransportResponse(status_code=getattr(resp, "status", 200), json_data=payload)


class MusesClient:
    """Client that fails closed when the service is unavailable."""

    def __init__(self, base_url: str, timeout: float = 5.0, transport: Transport | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._transport = transport or _UrllibTransport(self.base_url, timeout)
        self._status = ClientStatus(available=True, degraded=False, ui_state="active")

    @property
    def status(self) -> ClientStatus:
        return self._status

    def close(self) -> None:
        return None

    def _degrade(self, reason: str, error: str | None = None) -> ClientStatus:
        self._status = ClientStatus(available=False, degraded=True, ui_state="grayed", reason=reason, error=error)
        return self._status

    def _request_json(self, method: str, path: str, json: dict[str, Any] | None = None) -> ClientResult:
        try:
            response = self._transport.request(method, path, json=json)
            response.raise_for_status()
            self._status = ClientStatus(available=True, degraded=False, ui_state="active")
            return ClientResult(ok=True, data=response.json(), status=self._status)
        except (TimeoutError, OSError, URLError) as exc:
            return ClientResult(ok=False, data=None, status=self._degrade("service_unavailable", str(exc)))
        except HTTPError as exc:
            return ClientResult(ok=False, data=None, status=self._degrade(f"http_{exc.code}", str(exc)))
        except Exception as exc:
            # transport-agnostic fallback for custom transports
            message = str(exc)
            if message.startswith("HTTP ") and message[5:].isdigit():
                return ClientResult(ok=False, data=None, status=self._degrade(f"http_{message[5:]}", message))
            return ClientResult(ok=False, data=None, status=self._degrade("service_unavailable", message))

    def health(self) -> ClientResult:
        return self._request_json("GET", "/v1/health")

    def analyze_consistency_scene(self, *, scene: dict[str, Any]) -> ClientResult:
        return self._request_json("POST", "/v1/analyze/consistency_scene", json=scene)

    def analyze_consistency_session(self, *, session: dict[str, Any]) -> ClientResult:
        return self._request_json("POST", "/v1/analyze/consistency_session", json=session)

    def analyze_summary(self, *, payload: dict[str, Any]) -> ClientResult:
        return self._request_json("POST", "/v1/analyze/summary", json=payload)

    def analyze_federated_links(self, *, payload: dict[str, Any]) -> ClientResult:
        return self._request_json("POST", "/v1/analyze/federated_links", json=payload)

    def __enter__(self) -> "MusesClient":
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return None
