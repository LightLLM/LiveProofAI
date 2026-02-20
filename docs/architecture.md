# LiveProof AI – Architecture

## High-level flow

```
┌─────────────┐     POST /verify      ┌─────────────┐
│   Next.js   │ ────────────────────► │   FastAPI   │
│   (web)     │                       │   (api)     │
└─────────────┘                       └──────┬──────┘
       │                                     │
       │ GET /topic/:topic/compare            │ 1) You.com Search API
       │ GET /sources/top                     │    (or stub)
       │                                     ▼
       │                            ┌─────────────────┐
       │                            │  Normalize     │
       │                            │  citations     │
       │                            └────────┬───────┘
       │                                     │
       │                                     ▼
       │                            ┌─────────────────┐
       │                            │  Build claims  │
       │                            │  + reliability │
       │                            └────────┬───────┘
       │                                     │
       │                                     ▼
       │                            ┌─────────────────┐
       │                            │  Sanity store   │
       │                            │  (topic,        │
       │                            │   session,      │
       │                            │   claim, source)│
       │                            └─────────────────┘
       │
       └──────────────────────────► GROQ queries for
                                    compare & top sources
```

## Components

| Component | Role |
|-----------|------|
| **Web (Next.js)** | Landing (search + Verify & Answer), result view (answer, score, evidence, claim graph), history (compare by topic), admin (top sources, GROQ notes). |
| **API (FastAPI)** | `/verify` (You.com → claims → reliability → Sanity), `/execute` (code/PDF/config in-memory), `/session/{id}`, `/topic/{topic}/compare`, `/sources/top`. |
| **You.com** | Live search with citations; stubbed when `YOU_STUB=true` or no `YOU_API_KEY`. |
| **Sanity** | Structured content: topic, session, claim, source (and optional claimEdge). Enables compare-by-topic, top sources, contradictions. |
| **Worker (optional)** | GPU node: embedding service (stub or sentence-transformers); logs GPU usage. |

## Data model (Sanity)

- **topic** – slug, title.
- **session** – references topic; question, answer, reliabilityScore, canExecute, claims[], createdAt.
- **claim** – references session, topic; text, stance (support/oppose/neutral), sources[].
- **source** – url (dedupe by url hash), title, snippet, sourceName.
- **claimEdge** (optional) – fromClaim, toClaim, relation (supports/opposes) for contradiction view.

Relationships: session → topic; claim → session, topic, sources[]; source is shared across sessions.

## Reliability and execute

- Reliability is computed from number of claims, number of citations, and average claim confidence (see `verification.py`).
- Threshold: 0.65. Only when `reliability_score >= 0.65` and mode is `execute` can the user call `/execute`.
- Execute returns in-memory artifacts only (no shell or filesystem execution).

## LKE deployment

- **Web** and **API** behind Ingress (e.g. NGINX, TLS via cert-manager).
- **Worker** optional: deploy on GPU node pool with `nvidia.com/gpu` limit; use NVIDIA device plugin.
