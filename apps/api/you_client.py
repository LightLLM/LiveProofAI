"""
You.com API client for live web search with citations.
Supports stubbed mode when YOU_API_KEY is not set (for local/dev).
"""
import os
import hashlib
import uuid
from typing import Optional

import httpx

# Normalized citation as used across the app
Citation = dict  # { title, url, snippet, published_at?, source_name? }
STUB_MODE = os.environ.get("YOU_STUB", "true").lower() in ("1", "true", "yes")
YOU_API_KEY = os.environ.get("YOU_API_KEY", "")
YOU_BASE = "https://api.you.com/v1"


class StubMode:
    """Stub result shape for development when You.com API is not available."""
    @staticmethod
    def search(query: str) -> list[Citation]:
        return [
            {
                "title": "Example: Python asyncio documentation",
                "url": "https://docs.python.org/3/library/asyncio.html",
                "snippet": "asyncio is used as a foundation for multiple Python asynchronous frameworks.",
                "published_at": None,
                "source_name": "Python Docs",
            },
            {
                "title": "Example: FastAPI Concurrency",
                "url": "https://fastapi.tiangolo.com/async/",
                "snippet": "FastAPI supports async def endpoints for non-blocking I/O.",
                "published_at": None,
                "source_name": "FastAPI",
            },
            {
                "title": "Example: HTTPX async client",
                "url": "https://www.python-httpx.org/async/",
                "snippet": "Use httpx.AsyncClient() for async HTTP requests.",
                "published_at": None,
                "source_name": "HTTPX",
            },
        ]


def _normalize_citation(raw: dict) -> Citation:
    """Map You.com result item to our citation shape."""
    return {
        "title": raw.get("title") or raw.get("name") or "",
        "url": raw.get("url") or raw.get("link") or "",
        "snippet": raw.get("snippet") or raw.get("description") or raw.get("body") or "",
        "published_at": raw.get("published_at") or raw.get("date"),
        "source_name": raw.get("source") or raw.get("source_name"),
    }


class YouClient:
    """Minimal You.com Search API client with citation-backed results."""

    def __init__(self, api_key: Optional[str] = None, stub: Optional[bool] = None):
        self.api_key = api_key or YOU_API_KEY
        self.stub = stub if stub is not None else (not self.api_key or STUB_MODE)
        self.base = YOU_BASE

    async def search(self, query: str) -> list[Citation]:
        """Fetch search results; return normalized citations. Uses stub when no API key."""
        if self.stub:
            return StubMode.search(query)

        async with httpx.AsyncClient(timeout=15.0) as client:
            # You.com Search API (typical pattern: GET with query and API key header)
            resp = await client.get(
                f"{self.base}/search",
                params={"query": query},
                headers={"X-API-Key": self.api_key} if self.api_key else {},
            )
            resp.raise_for_status()
            data = resp.json()

        # Normalize: You.com may return results in different shapes
        citations: list[Citation] = []
        for item in data.get("results", data.get("web_results", data.get("results", []))):
            if isinstance(item, dict) and (item.get("url") or item.get("link")):
                citations.append(_normalize_citation(item))
        if not citations and isinstance(data.get("results"), list):
            for item in data["results"]:
                if isinstance(item, dict):
                    citations.append(_normalize_citation(item))
        return citations[:15]  # cap for response size
