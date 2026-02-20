"""
Sanity content store for LiveProof AI.
Stores: topic, session, claim, source; supports GROQ for compare, top sources, contradictions.
Uses Sanity HTTP API (documents create/patch) when SANITY_PROJECT_ID and SANITY_TOKEN are set.
"""
import os
import hashlib
import uuid
from typing import Optional

import httpx

SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_TOKEN = os.environ.get("SANITY_TOKEN", "")  # write token for mutations
SANITY_API_VERSION = "v2024-01-01"
BASE = f"https://{SANITY_PROJECT_ID}.api.sanity.io/{SANITY_API_VERSION}"


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


class SanityStore:
    def __init__(
        self,
        project_id: Optional[str] = None,
        dataset: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.project_id = project_id or SANITY_PROJECT_ID
        self.dataset = dataset or SANITY_DATASET
        self.token = token or SANITY_TOKEN
        self.enabled = bool(self.project_id and self.token)
        self.base = f"https://{self.project_id}.api.sanity.io/{SANITY_API_VERSION}"

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def _mutate(self, payload: dict) -> dict:
        if not self.enabled:
            return {}
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                f"{self.base}/data/mutate/{self.dataset}",
                headers=self._headers(),
                json=payload,
            )
            r.raise_for_status()
            return r.json()

    def _query(self, query: str, params: Optional[dict] = None) -> list:
        if not self.enabled:
            return []
        with httpx.Client(timeout=10.0) as client:
            r = client.get(
                f"{self.base}/data/query/{self.dataset}",
                params={"query": query, **(params or {})},
                headers=self._headers() if self.token else {},
            )
            r.raise_for_status()
            data = r.json()
            return data.get("result", [])

    def upsert_verification_result(self, result: dict) -> None:
        """Persist verification result as topic, session, claims, sources."""
        session_id = result.get("session_id") or str(uuid.uuid4())
        topic_slug = (result.get("topic") or "general").replace(" ", "-").lower()[:50]
        transactions = []

        # 1) Ensure topic exists
        topic_id = f"topic-{topic_slug}"
        transactions.append({
            "createOrReplace": {
                "_id": topic_id,
                "_type": "topic",
                "slug": topic_slug,
                "title": result.get("topic") or "General",
            }
        })

        # 2) Upsert sources (dedupe by url hash)
        citation_ids = []
        for c in result.get("citations", []):
            url = c.get("url", "")
            if not url:
                continue
            ref_id = f"source-{_url_hash(url)}"
            transactions.append({
                "createOrReplace": {
                    "_id": ref_id,
                    "_type": "source",
                    "url": url,
                    "title": c.get("title"),
                    "snippet": c.get("snippet"),
                    "sourceName": c.get("source_name"),
                }
            })
            citation_ids.append({"_type": "reference", "_ref": ref_id})

        # 3) Create claims with references to session, topic, sources
        claim_refs = []
        for i, cl in enumerate(result.get("claims", [])):
            claim_id = f"claim-{session_id}-{i}"
            refs = []
            for cid in cl.get("citation_ids", []):
                # citation_ids in result may be indices or url hashes
                if isinstance(cid, int) and 0 <= cid < len(result.get("citations", [])):
                    u = result["citations"][cid].get("url", "")
                    if u:
                        refs.append({"_type": "reference", "_ref": f"source-{_url_hash(u)}"})
                elif isinstance(cid, str) and cid.startswith("source-"):
                    refs.append({"_type": "reference", "_ref": cid})
            transactions.append({
                "createOrReplace": {
                    "_id": claim_id,
                    "_type": "claim",
                    "session": {"_type": "reference", "_ref": session_id},
                    "topic": {"_type": "reference", "_ref": topic_id},
                    "text": cl.get("text", ""),
                    "stance": cl.get("stance", "neutral"),
                    "sources": refs,
                }
            })
            claim_refs.append({"_type": "reference", "_ref": claim_id})

        # 4) Session document
        transactions.append({
            "createOrReplace": {
                "_id": session_id,
                "_type": "session",
                "topic": {"_type": "reference", "_ref": topic_id},
                "question": result.get("question", ""),
                "answer": result.get("answer", ""),
                "reliabilityScore": result.get("reliability_score", 0),
                "canExecute": result.get("can_execute", False),
                "claims": claim_refs,
                "createdAt": result.get("created_at") or "",
            }
        })

        for tx in transactions:
            self._mutate({"mutations": [tx]})

    def get_session(self, session_id: str) -> Optional[dict]:
        """Fetch session by ID and hydrate for API response."""
        q = f'*[_id == "{session_id}"][0]{{ _id, question, answer, reliabilityScore, canExecute, topic->, claims[]->{{ _id, text, stance, sources[]->{{ _id, url, title, snippet, sourceName }} }} }}'
        result = self._query(q)
        if result is None:
            return None
        first = result[0] if isinstance(result, list) and len(result) > 0 else (result if isinstance(result, dict) else None)
        if not first:
            return None
        if not first:
            return None
        # Map to our response shape
        claims = []
        citations_map = {}
        for c in first.get("claims") or []:
            srcs = c.get("sources") or []
            citation_ids = []
            for s in srcs:
                ref_id = s.get("_id")
                if ref_id and ref_id not in citations_map:
                    citations_map[ref_id] = {
                        "title": s.get("title") or "",
                        "url": s.get("url") or "",
                        "snippet": s.get("snippet") or "",
                        "source_name": s.get("sourceName"),
                    }
                if ref_id:
                    citation_ids.append(ref_id)
            claims.append({
                "id": c.get("_id"),
                "text": c.get("text"),
                "stance": c.get("stance"),
                "citation_ids": citation_ids,
            })
        return {
            "session_id": first.get("_id"),
            "question": first.get("question"),
            "answer": first.get("answer"),
            "reliability_score": first.get("reliabilityScore"),
            "can_execute": first.get("can_execute"),
            "claims": claims,
            "citations": list(citations_map.values()),
            "topic": first.get("topic", {}).get("title") if isinstance(first.get("topic"), dict) else None,
            "created_at": first.get("createdAt"),
        }

    def compare_sessions_by_topic(self, topic: str) -> list[dict]:
        """GROQ: sessions for same topic, for compare view."""
        slug = topic.replace(" ", "-").lower()[:50]
        q = '''*[_type == "session" && topic->slug == $slug] | order(createdAt desc) {
            _id, question, answer, reliabilityScore, createdAt,
            "claims_count": count(claims)
        }'''
        out = self._query(q, {"$slug": slug})
        return [
            {
                "session_id": s["_id"],
                "question": s.get("question"),
                "answer": s.get("answer"),
                "reliability_score": s.get("reliabilityScore"),
                "created_at": s.get("createdAt"),
                "claims_count": s.get("claims_count", 0),
            }
            for s in (out if isinstance(out, list) else [out])
        ]

    def get_top_sources(self, limit: int = 20) -> list[dict]:
        """GROQ: top cited sources across all sessions."""
        q = '''*[_type == "source"] {
            _id, url, title,
            "citation_count": count(*[_type == "claim" && references(^._id)])
        } | order(citation_count desc) [0...$limit] { url, title, citation_count }'''
        out = self._query(q, {"$limit": limit})
        if not isinstance(out, list):
            out = [out] if out else []
        return [{"url": s.get("url"), "title": s.get("title"), "citation_count": s.get("citation_count", 0)} for s in out]

    def get_contradictions(self, topic: Optional[str] = None) -> list[dict]:
        """GROQ: claims with opposing stance for same topic (claimEdge or stance)."""
        q = '''*[_type == "claim" && stance != "neutral"] {
            _id, text, stance, topic->{ _id, slug },
            "session_id": session._ref
        }'''
        out = self._query(q)
        if not isinstance(out, list):
            out = [out] if out else []
        by_topic = {}
        for c in out:
            t = (c.get("topic") or {}).get("slug") or "general"
            by_topic.setdefault(t, []).append(c)
        pairs = []
        for t, claims in by_topic.items():
            if topic and t != topic:
                continue
            supports = [c for c in claims if c.get("stance") == "support"]
            opposes = [c for c in claims if c.get("stance") == "oppose"]
            for a in supports:
                for b in opposes:
                    pairs.append({
                        "topic": t,
                        "support_claim": a.get("text"),
                        "oppose_claim": b.get("text"),
                        "support_id": a.get("_id"),
                        "oppose_id": b.get("_id"),
                    })
        return pairs
