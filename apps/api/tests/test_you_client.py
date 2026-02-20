"""Unit tests for You.com client: stub and citation normalization."""
import pytest
from you_client import YouClient, StubMode, _normalize_citation


def test_normalize_citation():
    raw = {
        "title": "My Title",
        "url": "https://example.com",
        "snippet": "A snippet.",
        "published_at": "2024-01-01",
        "source": "Example",
    }
    c = _normalize_citation(raw)
    assert c["title"] == "My Title"
    assert c["url"] == "https://example.com"
    assert c["snippet"] == "A snippet."
    assert c["published_at"] == "2024-01-01"
    assert c["source_name"] == "Example"


def test_normalize_citation_alternate_keys():
    raw = {"name": "Name", "link": "https://link.com", "description": "Desc", "date": "2023-01-01"}
    c = _normalize_citation(raw)
    assert c["title"] == "Name"
    assert c["url"] == "https://link.com"
    assert c["snippet"] == "Desc"
    assert c["published_at"] == "2023-01-01"


def test_normalize_citation_missing_fields():
    c = _normalize_citation({})
    assert c["title"] == ""
    assert c["url"] == ""
    assert c["snippet"] == ""


def test_stub_mode_search_returns_list():
    result = StubMode.search("anything")
    assert isinstance(result, list)
    assert len(result) >= 1
    for item in result:
        assert "url" in item
        assert "title" in item
        assert "snippet" in item


def test_you_client_stub_returns_same_shape():
    client = YouClient(stub=True)
    assert client.stub is True


@pytest.mark.asyncio
async def test_you_client_search_stub_returns_citations():
    client = YouClient(stub=True)
    citations = await client.search("Python asyncio")
    assert isinstance(citations, list)
    assert len(citations) == 3
    for c in citations:
        assert "url" in c and c["url"].startswith("http")
        assert "title" in c
        assert "snippet" in c
