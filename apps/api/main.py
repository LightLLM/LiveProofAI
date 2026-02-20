"""
LiveProof AI - FastAPI backend.
Endpoints: /verify, /execute, /session/{id}, /topic/{topic}/compare, /sources/top
"""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from you_client import YouClient, StubMode
from sanity_store import SanityStore
from verification import run_verification_pipeline, run_execute

RELIABILITY_THRESHOLD = 0.65


# --- Request/Response models ---
class VerifyRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    mode: str = Field(default="answer", pattern="^(answer|execute)$")
    topic: Optional[str] = Field(default=None, max_length=200)


class VerifyResponse(BaseModel):
    answer: str
    reliability_score: float
    claims: list[dict]
    citations: list[dict]
    session_id: str
    can_execute: bool
    next_question: Optional[str] = None
    topic: Optional[str] = None


class ExecuteRequest(BaseModel):
    session_id: str
    action_type: str = Field(..., pattern="^(code_snippet|pdf_report|config)$")


class ExecuteResponse(BaseModel):
    artifact: str
    artifact_type: str  # "code" | "pdf_base64" | "config"
    logs: list[str]
    safety_notes: list[str]


# --- In-memory session store (fallback when Sanity not configured) ---
_sessions: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init You client and Sanity store from env
    app.state.you_client = YouClient()
    app.state.sanity = SanityStore()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="LiveProof AI API",
    description="Citation-backed technical Q&A with reliability scoring",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session(session_id: str) -> Optional[dict]:
    if session_id in _sessions:
        return _sessions[session_id]
    sanity = app.state.sanity
    if sanity.enabled:
        doc = sanity.get_session(session_id)
        if doc:
            return doc
    return None


@app.post("/verify", response_model=VerifyResponse)
async def verify(req: VerifyRequest):
    """Run verification pipeline: You.com search -> claims -> reliability -> Sanity."""
    you_client: YouClient = app.state.you_client
    sanity: SanityStore = app.state.sanity

    result = await run_verification_pipeline(
        question=req.question,
        mode=req.mode,
        topic=req.topic,
        you_client=you_client,
        sanity_store=sanity,
    )
    # Persist to in-memory for quick lookup
    _sessions[result["session_id"]] = result
    # Persist to Sanity when enabled
    if sanity.enabled:
        sanity.upsert_verification_result(result)

    return VerifyResponse(
        answer=result["answer"],
        reliability_score=result["reliability_score"],
        claims=result["claims"],
        citations=result["citations"],
        session_id=result["session_id"],
        can_execute=result["can_execute"],
        next_question=result.get("next_question"),
        topic=result.get("topic"),
    )


@app.post("/execute", response_model=ExecuteResponse)
async def execute(req: ExecuteRequest):
    """Execute a safe action (code snippet, PDF report, config) for a verified session."""
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.get("can_execute"):
        raise HTTPException(
            status_code=400,
            detail="Execution not allowed: reliability below threshold. Ask for clarification.",
        )
    outcome = run_execute(
        session=session,
        action_type=req.action_type,
    )
    return ExecuteResponse(
        artifact=outcome["artifact"],
        artifact_type=outcome["artifact_type"],
        logs=outcome["logs"],
        safety_notes=outcome["safety_notes"],
    )


@app.get("/session/{session_id}")
async def get_session_endpoint(session_id: str):
    """Get a session by ID (from memory or Sanity)."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/topic/{topic}/compare")
async def topic_compare(topic: str):
    """Compare sessions for the same topic (from Sanity structured content)."""
    sanity: SanityStore = app.state.sanity
    if not sanity.enabled:
        return {"topic": topic, "sessions": [], "message": "Sanity not configured; no compare data."}
    sessions = sanity.compare_sessions_by_topic(topic)
    return {"topic": topic, "sessions": sessions}


@app.get("/sources/top")
async def sources_top(limit: int = 20):
    """Top cited sources across all sessions (from Sanity)."""
    sanity: SanityStore = app.state.sanity
    if not sanity.enabled:
        return {"sources": [], "message": "Sanity not configured."}
    sources = sanity.get_top_sources(limit=limit)
    return {"sources": sources}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "liveproof-api"}
