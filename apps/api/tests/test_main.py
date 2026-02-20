"""API endpoint tests: /verify, /execute, /session, /topic/compare, /sources, /health."""
import pytest
from fastapi.testclient import TestClient
from main import app, _sessions


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear in-memory sessions between tests so they don't leak."""
    _sessions.clear()
    yield
    _sessions.clear()


@pytest.fixture
def client():
    """TestClient with lifespan so app.state.you_client and app.state.sanity are set."""
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "liveproof-api"


def test_verify_returns_200_and_shape(client: TestClient):
    r = client.post(
        "/verify",
        json={"question": "How does Python asyncio work?", "mode": "answer"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    assert "answer" in data
    assert "reliability_score" in data
    assert "claims" in data
    assert "citations" in data
    assert "can_execute" in data
    assert isinstance(data["reliability_score"], (int, float))
    assert isinstance(data["claims"], list)
    assert isinstance(data["citations"], list)


def test_verify_with_topic(client: TestClient):
    r = client.post(
        "/verify",
        json={
            "question": "What is FastAPI?",
            "mode": "answer",
            "topic": "python-asyncio",
        },
    )
    assert r.status_code == 200
    assert r.json().get("topic") == "python-asyncio"


def test_verify_validation_error_empty_question(client: TestClient):
    r = client.post(
        "/verify",
        json={"question": "", "mode": "answer"},
    )
    assert r.status_code == 422


def test_verify_validation_error_invalid_mode(client: TestClient):
    r = client.post(
        "/verify",
        json={"question": "Hi", "mode": "invalid"},
    )
    assert r.status_code == 422


def test_session_get_404_when_missing(client: TestClient):
    r = client.get("/session/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert "not found" in r.json().get("detail", "").lower()


def test_verify_then_get_session(client: TestClient):
    verify_r = client.post(
        "/verify",
        json={"question": "Test question", "mode": "execute"},
    )
    assert verify_r.status_code == 200
    session_id = verify_r.json()["session_id"]
    session_r = client.get(f"/session/{session_id}")
    assert session_r.status_code == 200
    data = session_r.json()
    assert data["session_id"] == session_id
    assert data["question"] == "Test question"


def test_execute_404_when_session_missing(client: TestClient):
    r = client.post(
        "/execute",
        json={"session_id": "00000000-0000-0000-0000-000000000000", "action_type": "code_snippet"},
    )
    assert r.status_code == 404


def test_execute_400_when_can_execute_false(client: TestClient):
    verify_r = client.post(
        "/verify",
        json={"question": "x", "mode": "answer"},
    )
    assert verify_r.status_code == 200
    session_id = verify_r.json()["session_id"]
    _sessions[session_id] = {**_sessions[session_id], "can_execute": False}
    r = client.post(
        "/execute",
        json={"session_id": session_id, "action_type": "code_snippet"},
    )
    assert r.status_code == 400
    assert "threshold" in r.json().get("detail", "").lower() or "clarification" in r.json().get("detail", "").lower()


def test_execute_code_snippet_success(client: TestClient):
    verify_r = client.post(
        "/verify",
        json={"question": "Python async", "mode": "execute"},
    )
    assert verify_r.status_code == 200
    session_id = verify_r.json()["session_id"]
    if not verify_r.json().get("can_execute"):
        _sessions[session_id] = {**_sessions[session_id], "can_execute": True}
    r = client.post(
        "/execute",
        json={"session_id": session_id, "action_type": "code_snippet"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["artifact_type"] == "code"
    assert "artifact" in data
    assert "Verified context" in data["artifact"] or "Implement" in data["artifact"]
    assert "logs" in data
    assert "safety_notes" in data


def test_execute_pdf_report_returns_base64(client: TestClient):
    verify_r = client.post("/verify", json={"question": "Test", "mode": "execute"})
    assert verify_r.status_code == 200
    session_id = verify_r.json()["session_id"]
    _sessions[session_id] = {**_sessions[session_id], "can_execute": True}
    r = client.post(
        "/execute",
        json={"session_id": session_id, "action_type": "pdf_report"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["artifact_type"] == "pdf_base64"
    assert len(data["artifact"]) > 0
    import base64
    decoded = base64.b64decode(data["artifact"])
    assert decoded[:4] == b"%PDF"


def test_execute_config_success(client: TestClient):
    verify_r = client.post("/verify", json={"question": "Config", "mode": "execute"})
    assert verify_r.status_code == 200
    session_id = verify_r.json()["session_id"]
    _sessions[session_id] = {**_sessions[session_id], "can_execute": True}
    r = client.post(
        "/execute",
        json={"session_id": session_id, "action_type": "config"},
    )
    assert r.status_code == 200
    assert r.json()["artifact_type"] == "config"
    assert "LiveProof" in r.json()["artifact"]


def test_execute_validation_invalid_action_type(client: TestClient):
    r = client.post(
        "/execute",
        json={"session_id": "some-id", "action_type": "run_shell"},
    )
    assert r.status_code == 422


def test_topic_compare_returns_structure_when_sanity_disabled(client: TestClient):
    r = client.get("/topic/python-asyncio/compare")
    assert r.status_code == 200
    data = r.json()
    assert "sessions" in data
    assert "topic" in data
    assert data["topic"] == "python-asyncio"
    assert isinstance(data["sessions"], list)


def test_sources_top_returns_structure_when_sanity_disabled(client: TestClient):
    r = client.get("/sources/top")
    assert r.status_code == 200
    data = r.json()
    assert "sources" in data
    assert isinstance(data["sources"], list)


def test_sources_top_accepts_limit_param(client: TestClient):
    r = client.get("/sources/top?limit=5")
    assert r.status_code == 200
    assert "sources" in r.json()
