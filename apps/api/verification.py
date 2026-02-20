"""
Verification pipeline: search -> normalize citations -> build claims -> reliability score -> persist.
Execute: generate code snippet / PDF report / config from session (in-memory only).
"""
import uuid
import base64
from io import BytesIO
from datetime import datetime, timezone

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

RELIABILITY_THRESHOLD = 0.65


def _build_claims_from_citations(citations: list[dict]) -> tuple[list[dict], list[dict]]:
    """Convert citations into short factual claims and dedupe citations by url."""
    seen_urls = set()
    unique_citations = []
    url_to_idx = {}
    for c in citations:
        url = c.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        url_to_idx[url] = len(unique_citations)
        unique_citations.append({
            "title": c.get("title", ""),
            "url": url,
            "snippet": c.get("snippet", ""),
            "published_at": c.get("published_at"),
            "source_name": c.get("source_name"),
        })

    claims = []
    for i, c in enumerate(unique_citations[:10]):
        snippet = (c.get("snippet") or "")[:200]
        if not snippet:
            snippet = c.get("title", "No snippet")
        claim_id = f"cl-{i}"
        claims.append({
            "id": claim_id,
            "text": snippet,
            "stance": "neutral",
            "citation_ids": [i],
            "confidence": 0.85,
        })
    return claims, unique_citations


def _compute_reliability(claims: list[dict], citations: list[dict]) -> float:
    """Simple reliability: more claims + more citations -> higher score. Cap at 0.95."""
    n_claims = max(len(claims), 1)
    n_citations = max(len(citations), 1)
    score = 0.3 + 0.3 * min(n_claims / 5, 1) + 0.3 * min(n_citations / 5, 1)
    avg_conf = sum(c.get("confidence", 0.8) for c in claims) / n_claims
    score += 0.1 * avg_conf
    return round(min(score, 0.95), 2)


async def run_verification_pipeline(
    question: str,
    mode: str,
    topic: str | None,
    you_client,
    sanity_store,
) -> dict:
    """Run You.com search -> claims -> reliability -> build response."""
    raw_citations = await you_client.search(question)
    claims, citations = _build_claims_from_citations(raw_citations)
    reliability_score = _compute_reliability(claims, citations)
    can_execute = reliability_score >= RELIABILITY_THRESHOLD and mode == "execute"
    session_id = str(uuid.uuid4())

    # Build a short answer from top claim snippets
    answer_parts = [c.get("text", "")[:150] for c in claims[:3] if c.get("text")]
    answer = " ".join(answer_parts).strip() or "Insufficient evidence to form a confident answer."

    next_question = None
    if not can_execute and mode == "execute":
        next_question = "Reliability is below threshold. Could you narrow your question or add context so we can gather more evidence?"

    return {
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "reliability_score": reliability_score,
        "claims": claims,
        "citations": citations,
        "can_execute": can_execute,
        "next_question": next_question,
        "topic": topic or "general",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def run_execute(session: dict, action_type: str) -> dict:
    """Produce artifact in-memory only: code_snippet | pdf_report | config."""
    logs = []
    safety_notes = ["All artifacts generated in-memory; no shell or file system execution."]
    question = session.get("question", "")
    answer = session.get("answer", "")
    topic = session.get("topic", "general")

    if action_type == "code_snippet":
        logs.append("Generating code snippet from verified context.")
        artifact = f'# Verified context: {topic}\n# Q: {question[:80]}...\n\n"""\n{answer[:500]}\n"""\n\ndef main():\n    # Implement based on verified evidence above\n    pass\n\nif __name__ == "__main__":\n    main()\n'
        return {
            "artifact": artifact,
            "artifact_type": "code",
            "logs": logs,
            "safety_notes": safety_notes,
        }

    if action_type == "pdf_report":
        logs.append("Generating PDF report.")
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("LiveProof AI – Verification Report", styles["Title"]),
            Spacer(1, 12),
            Paragraph(f"<b>Topic:</b> {topic}", styles["Normal"]),
            Paragraph(f"<b>Question:</b> {question}", styles["Normal"]),
            Spacer(1, 12),
            Paragraph("<b>Answer</b>", styles["Heading2"]),
            Paragraph(answer.replace("\n", "<br/>"), styles["Normal"]),
            Spacer(1, 12),
            Paragraph("<b>Reliability Score:</b> " + str(session.get("reliability_score", 0)), styles["Normal"]),
        ]
        doc.build(story)
        pdf_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {
            "artifact": pdf_b64,
            "artifact_type": "pdf_base64",
            "logs": logs,
            "safety_notes": safety_notes,
        }

    if action_type == "config":
        logs.append("Generating config file.")
        artifact = f"# LiveProof AI – config for topic: {topic}\nquestion = \"{question[:200]}\"\nreliability_score = {session.get('reliability_score', 0)}\nanswer_preview = \"\"\"{answer[:300]}\"\"\"\n"
        return {
            "artifact": artifact,
            "artifact_type": "config",
            "logs": logs,
            "safety_notes": safety_notes,
        }

    return {
        "artifact": "",
        "artifact_type": "config",
        "logs": logs,
        "safety_notes": safety_notes + ["Unknown action_type."],
    }
