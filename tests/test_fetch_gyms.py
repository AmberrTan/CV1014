import json

import pytest

import scripts.fetch_gyms as fetch_gyms


class FakeResponse:
    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = payload
        if isinstance(payload, (dict, list)):
            self.text = json.dumps(payload)
        else:
            self.text = str(payload)

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if not self._responses:
            raise RuntimeError("No more fake responses")
        return self._responses.pop(0)


def test_request_json_retries_on_429(monkeypatch):
    responses = [
        FakeResponse(429, {"error": "too many"}),
        FakeResponse(200, {"ok": True}),
    ]
    session = FakeSession(responses)
    monkeypatch.setattr(fetch_gyms.time, "sleep", lambda *_: None)

    payload = fetch_gyms.request_json(
        session,
        "GET",
        "https://example.com",
        timeout=5,
        retries=2,
        backoff_seconds=0.1,
        extra_backoff_seconds=0.0,
    )

    assert payload == {"ok": True}
    assert len(session.calls) == 2


def test_request_json_raises_on_non_retryable_status():
    responses = [FakeResponse(400, {"error": "bad request"})]
    session = FakeSession(responses)

    with pytest.raises(RuntimeError, match="400"):
        fetch_gyms.request_json(
            session,
            "GET",
            "https://example.com",
            timeout=5,
            retries=2,
            backoff_seconds=0.1,
            extra_backoff_seconds=0.0,
        )


def test_build_osm_search_queries_dedupes():
    gym = {
        "gym_name": "Pulse Fitness",
        "address": "1 Example Road",
        "area": "Central",
    }
    queries = fetch_gyms.build_osm_search_queries(gym, country_hint="Singapore")

    assert queries[0].startswith("Pulse Fitness")
    assert len(queries) == len(set(queries))
