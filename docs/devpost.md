# Devpost – LiveProof AI

## Tagline

Citation-backed technical Q&A: verify with live evidence, explore a claim graph, and run safe actions only when reliability is high.

## Inspiration

We wanted a system that doesn’t just answer—it **proves** answers with live web evidence and makes the proof inspectable. Technical users can see exactly which claims and sources back an answer and compare how answers for the same topic change over time. Execution (code snippet, PDF, config) is only allowed when evidence is strong enough.

## What it does

- **Verify & Answer:** User asks a technical question. The system calls the You.com API for live, citation-backed search, turns results into a structured **Claim Graph** (claims + sources), and stores it in **Sanity**. It computes a **reliability score** and returns an answer with evidence.
- **Structured content unlocks features:**  
  - “Show all claims supporting this answer” (Claim Graph in the UI).  
  - “Show all sources used across all sessions” (top sources from Sanity GROQ).  
  - “Compare answers for the same topic over time” (History → Compare by topic, Sanity GROQ).  
  - “Find contradictions” (claims with opposing stance for the same topic; schema + GROQ).
- **Execute only when safe:** If reliability is above a threshold, the user can request a **code snippet**, **PDF report**, or **config file**. These are generated in-memory and returned; we never execute arbitrary shell commands.

## How we built it

- **Frontend:** Next.js 14 + Tailwind; landing (search + Verify & Answer), result view (answer, reliability, evidence, claim graph), history (compare by topic), admin (top sources, GROQ).
- **Backend:** FastAPI with endpoints: `POST /verify`, `POST /execute`, `GET /session/{id}`, `GET /topic/{topic}/compare`, `GET /sources/top`.
- **You.com:** Minimal client for the You.com Search API; results normalized to citations (title, url, snippet, etc.) and used to build claims. Stub mode when no API key.
- **Sanity:** Content model: topic, session, claim, source, claimEdge. Sessions and claims are written on verify; GROQ powers compare-by-topic and top sources. Schema and content workflows supported by the **Sanity MCP** (https://mcp.sanity.io).
- **Deployment:** Kubernetes manifests for LKE (web, api, optional GPU worker), Ingress, ConfigMap, Secrets. Docker Compose for local one-command run.
- **GPU worker (optional):** Small service that can run embeddings (e.g. sentence-transformers with CUDA) on an LKE GPU node; stub included for when GPU is not in use.

## Challenges

- Aligning Sanity document IDs and references (session → topic, claim → session/topic/sources) with the API’s in-memory flow and GROQ queries.
- Designing a simple but meaningful reliability score from claims and citations without overfitting.
- Keeping execute strictly safe (in-memory only, no user-controlled shell or file writes).

## Accomplishments

- End-to-end flow: question → You.com → citations → claims → reliability → Sanity → response with evidence.
- Structured content that actually drives product features (compare, top sources, claim graph).
- Clear one-command local run (Docker Compose) and a path to one-command-style LKE deploy with docs.
- Devpost-ready narrative and demo script.

## What we learned

- Sanity’s references and GROQ make “compare sessions by topic” and “top cited sources” natural.
- Stubbing You.com and making Sanity optional keeps the app runnable without keys.
- Explicit “can_execute” and a threshold in the API keeps the UX and safety story simple.

## What’s next

- Real You.com production usage and more claim-extraction logic (e.g. LLM or rules).
- Contradiction detection UI using claim stance and claimEdge.
- Optional GPU worker in production with sentence-transformers for embeddings and logging GPU utilization.
- More execute artifact types and optional persistence (e.g. download-only PDFs).

## Try it

- **Local:** `git clone … && docker compose up -d` → http://localhost:3000.
- **Hosted:** [Link to your hosted demo].
- **Repo:** [Link to your open-source repo].

## Hackathon alignment

- **You.com:** We use the You.com API to deliver citation-backed search results.
- **Sanity:** Sanity is the content backend; the structured Claim Graph enables compare-by-topic, top sources, and contradictions. Schema and content operations are documented for use with the Sanity MCP.
- **Akamai/Linode:** We deploy on LKE (manifests in `infra/k8s/`); optional GPU worker for embeddings on a GPU node.
- **Open-source:** Repo includes README, setup, architecture, and demo script.
