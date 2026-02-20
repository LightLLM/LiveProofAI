# LiveProof AI

**Citation-backed technical Q&A with a Claim Graph and reliability scoring.** Ask a question → we fetch live web evidence (You.com), turn it into structured claims stored in Sanity, compute a reliability score, and only run safe actions (code snippet, PDF report, config) when reliability is above threshold.

## Quick start (one command)

```bash
# Clone and run with Docker Compose
git clone https://github.com/your-org/liveproof-ai.git && cd liveproof-ai
docker compose up -d
```

- **Web:** http://localhost:3000  
- **API:** http://localhost:8000  
- **API docs:** http://localhost:8000/docs  

No API keys required for stub mode (You.com and Sanity are optional).

## Testing

- **API (pytest):** `cd apps/api && pip install -r requirements.txt && python -m pytest tests -v`
- **Web (Jest):** `cd apps/web && npm install && npm test`
- **From repo root:** `npm run test:api` (API only; requires Python venv + deps in `apps/api`).

## Repo structure

```
liveproof-ai/
├── apps/
│   ├── api/          # FastAPI: /verify, /execute, /session, /topic/compare, /sources
│   ├── web/          # Next.js + Tailwind
│   └── worker/       # Optional GPU worker (embeddings)
├── packages/
│   └── shared/       # Shared TypeScript types
├── sanity/           # Sanity schema (topic, session, claim, source, claimEdge)
├── infra/
│   └── k8s/          # LKE manifests (web, api, worker, ingress)
├── docs/             # Architecture, demo script, Devpost
├── .mcp/             # Sanity MCP instructions
├── docker-compose.yml
└── README.md
```

## Local development (no Docker)

### API

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```

### Web

```bash
pnpm install
pnpm --filter @liveproof/shared build
pnpm --filter web dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` (default in code).

### Environment (API)

| Variable | Description |
|----------|-------------|
| `YOU_STUB` | `true` = use stub You.com results (default). `false` + `YOU_API_KEY` = real API. |
| `YOU_API_KEY` | You.com API key for live search. |
| `SANITY_PROJECT_ID` | Sanity project ID. |
| `SANITY_DATASET` | Dataset (default `production`). |
| `SANITY_TOKEN` | Sanity token (write) for persisting sessions/claims/sources. |

## Deploy to LKE (one-command style)

1. **Build and push images** (replace with your registry):

```bash
docker build -f apps/api/Dockerfile -t your-registry/liveproof-api:latest .
docker build -f apps/web/Dockerfile -t your-registry/liveproof-web:latest .
docker push your-registry/liveproof-api:latest
docker push your-registry/liveproof-web:latest
```

2. **Create namespace and secrets:**

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl create secret generic liveproof-secrets -n liveproof \
  --from-literal=YOU_API_KEY=xxx \
  --from-literal=SANITY_PROJECT_ID=xxx \
  --from-literal=SANITY_TOKEN=xxx
```

3. **Apply manifests:**

```bash
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/api-deployment.yaml
kubectl apply -f infra/k8s/web-deployment.yaml
kubectl apply -f infra/k8s/ingress.yaml
```

4. **Optional – GPU worker:** Install [NVIDIA device plugin](https://github.com/NVIDIA/k8s-device-plugin), then:

```bash
kubectl apply -f infra/k8s/worker-deployment.yaml
```

5. Point your Ingress hostnames (`liveproof.example.com`, `api.liveproof.example.com`) to your LKE load balancer and configure TLS (e.g. cert-manager).

See [docs/architecture.md](docs/architecture.md) and [docs/demo-script.md](docs/demo-script.md) for more.

## Features (structured content)

- **Show all claims supporting this answer** – Claim Graph in the result view and in Sanity.
- **Show all sources used across all sessions** – `/sources/top` and Admin page (Sanity GROQ).
- **Compare answers for the same topic over time** – History → Compare by topic (Sanity GROQ).
- **Find contradictions** – Claims with opposing stance for the same topic (Sanity schema + GROQ; API can expose via optional endpoint).

## Safety

- No arbitrary shell or command execution from user input.
- Execute mode only generates artifacts in-memory (code snippet, PDF bytes, config text) and returns them.

## License

MIT.
