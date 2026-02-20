"""Unit tests for verification pipeline and execute."""
import pytest
from verification import (
    _build_claims_from_citations,
    _compute_reliability,
    run_verification_pipeline,
    run_execute,
    RELIABILITY_THRESHOLD,
)


def test_build_claims_empty_citations():
    claims, citations = _build_claims_from_citations([])
    assert claims == []
    assert citations == []


def test_build_claims_dedupes_by_url():
    raw = [
        {"url": "https://a.com", "title": "A", "snippet": "Snippet A"},
        {"url": "https://a.com", "title": "A again", "snippet": "Duplicate"},
        {"url": "https://b.com", "title": "B", "snippet": "Snippet B"},
    ]
    claims, citations = _build_claims_from_citations(raw)
    assert len(citations) == 2
    assert len(claims) == 2
    urls = [c["url"] for c in citations]
    assert urls == ["https://a.com", "https://b.com"]


def test_build_claims_skips_empty_url():
    raw = [
        {"url": "", "title": "No URL", "snippet": "x"},
        {"url": "https://ok.com", "title": "OK", "snippet": "y"},
    ]
    claims, citations = _build_claims_from_citations(raw)
    assert len(citations) == 1
    assert citations[0]["url"] == "https://ok.com"
    assert len(claims) == 1
    assert claims[0]["citation_ids"] == [0]


def test_build_claims_shape():
    raw = [{"url": "https://x.com", "title": "X", "snippet": "Some text here."}]
    claims, citations = _build_claims_from_citations(raw)
    assert len(claims) == 1
    assert claims[0]["id"] == "cl-0"
    assert claims[0]["text"] == "Some text here."
    assert claims[0]["stance"] == "neutral"
    assert claims[0]["citation_ids"] == [0]
    assert claims[0].get("confidence") == 0.85
    assert citations[0]["url"] == "https://x.com"
    assert citations[0]["title"] == "X"


def test_compute_reliability_empty_claims():
    score = _compute_reliability([], [])
    assert 0 <= score <= 1


def test_compute_reliability_increases_with_claims_and_citations():
    one = _compute_reliability(
        [{"confidence": 0.8}],
        [{"url": "u"}],
    )
    five = _compute_reliability(
        [{"confidence": 0.8}] * 5,
        [{"url": f"u{i}"} for i in range(5)],
    )
    assert five >= one
    assert _compute_reliability([], []) <= 0.95


def test_compute_reliability_capped():
    many = _compute_reliability(
        [{"confidence": 1.0}] * 20,
        [{"url": f"u{i}"} for i in range(20)],
    )
    assert many <= 0.95


@pytest.mark.asyncio
async def test_run_verification_pipeline_returns_required_keys():
    class StubYou:
        async def search(self, q):
            return [
                {"url": "https://a.com", "title": "A", "snippet": "Snippet"},
            ]

    class StubSanity:
        enabled = False

    result = await run_verification_pipeline(
        question="Test?",
        mode="answer",
        topic=None,
        you_client=StubYou(),
        sanity_store=StubSanity(),
    )
    assert "session_id" in result
    assert "answer" in result
    assert "reliability_score" in result
    assert "claims" in result
    assert "citations" in result
    assert "can_execute" in result
    assert "topic" in result
    assert result["question"] == "Test?"
    assert result["topic"] == "general"
    assert result["can_execute"] == (result["reliability_score"] >= RELIABILITY_THRESHOLD)


@pytest.mark.asyncio
async def test_run_verification_pipeline_execute_mode_sets_next_question_when_low():
    class LowEvidenceYou:
        async def search(self, q):
            return [{"url": "https://one.com", "title": "One", "snippet": "Only one."}]

    result = await run_verification_pipeline(
        question="?",
        mode="execute",
        topic=None,
        you_client=LowEvidenceYou(),
        sanity_store=type("S", (), {"enabled": False})(),
    )
    if not result["can_execute"]:
        assert result.get("next_question") is not None
        assert "threshold" in result["next_question"].lower() or "evidence" in result["next_question"].lower()


def test_run_execute_code_snippet():
    session = {"question": "Q?", "answer": "A", "topic": "t", "reliability_score": 0.8}
    out = run_execute(session, "code_snippet")
    assert out["artifact_type"] == "code"
    assert "Verified context" in out["artifact"]
    assert "Q?" in out["artifact"]
    assert "safety_notes" in out
    assert any("in-memory" in n for n in out["safety_notes"])


def test_run_execute_pdf_report():
    session = {"question": "Q?", "answer": "A", "topic": "t", "reliability_score": 0.8}
    out = run_execute(session, "pdf_report")
    assert out["artifact_type"] == "pdf_base64"
    assert len(out["artifact"]) > 0
    import base64
    raw = base64.b64decode(out["artifact"])
    assert raw[:4] == b"%PDF"


def test_run_execute_config():
    session = {"question": "Q?", "answer": "A", "topic": "my-topic", "reliability_score": 0.7}
    out = run_execute(session, "config")
    assert out["artifact_type"] == "config"
    assert "my-topic" in out["artifact"]
    assert "reliability_score" in out["artifact"]


def test_run_execute_unknown_action_returns_safe():
    session = {"question": "Q", "answer": "A", "topic": "t"}
    out = run_execute(session, "unknown_type")
    assert out["artifact"] == ""
    assert "Unknown" in str(out["safety_notes"])
