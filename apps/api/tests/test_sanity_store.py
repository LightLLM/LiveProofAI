"""Unit tests for Sanity store (disabled mode and helpers)."""
import hashlib
from sanity_store import SanityStore, _url_hash


def test_url_hash():
    h = _url_hash("https://example.com/page")
    assert isinstance(h, str)
    assert len(h) == 16
    assert h == hashlib.sha256(b"https://example.com/page").hexdigest()[:16]


def test_sanity_store_disabled_when_no_credentials():
    store = SanityStore(project_id="", token="")
    assert store.enabled is False


def test_sanity_store_disabled_when_no_token():
    store = SanityStore(project_id="proj", token="")
    assert store.enabled is False


def test_sanity_store_enabled_when_both_set():
    store = SanityStore(project_id="proj", token="secret")
    assert store.enabled is True


def test_sanity_store_query_returns_empty_when_disabled():
    store = SanityStore(project_id="", token="")
    result = store._query("*[_type == 'session']")
    assert result == []


def test_sanity_store_compare_sessions_returns_empty_when_disabled():
    store = SanityStore(project_id="", token="")
    sessions = store.compare_sessions_by_topic("any-topic")
    assert sessions == []


def test_sanity_store_get_top_sources_returns_empty_when_disabled():
    store = SanityStore(project_id="", token="")
    sources = store.get_top_sources(limit=10)
    assert sources == []


def test_sanity_store_get_session_returns_none_when_disabled():
    store = SanityStore(project_id="", token="")
    doc = store.get_session("some-id")
    assert doc is None


def test_sanity_store_upsert_does_not_raise_when_disabled():
    store = SanityStore(project_id="", token="")
    store.upsert_verification_result({
        "session_id": "s1",
        "question": "Q?",
        "answer": "A",
        "reliability_score": 0.8,
        "claims": [{"id": "c1", "text": "T", "citation_ids": [0]}],
        "citations": [{"url": "https://x.com", "title": "X", "snippet": "S"}],
        "can_execute": True,
        "topic": "general",
    })
    # No network call; should not raise
