# LiveProof AI – 2–4 minute demo script

## 1. Landing (30 s)

- Open the app (localhost:3000 or hosted demo).
- Show the search box and “Verify & Answer”.
- Explain: “You ask a technical question; we fetch live evidence, build a claim graph, and only run actions when reliability is high.”

## 2. Verify & Answer (1 min)

- Enter a question, e.g.: **“How do I use async/await in Python with FastAPI?”**
- Optional: set topic to **“python-asyncio”** (for compare later).
- Click **Verify & Answer**.
- Show:
  - **Answer** (synthesized from evidence).
  - **Reliability score** (e.g. 75%).
  - **Evidence panel** – citations with titles, URLs, snippets.
  - **Claim Graph** – claims linked to sources.

## 3. Execute (optional, 30 s)

- Switch mode to **“Answer + allow execute”** and verify again (or use same session if already above threshold).
- Click **code_snippet** (or PDF report / config).
- Show the generated artifact (snippet or download link) and note: “All in-memory; no shell execution.”

## 4. History & Compare (45 s)

- Go to **History**.
- Enter topic **“python-asyncio”** (or the one you used).
- Click **Compare**.
- Show sessions for that topic: “Same topic over time, powered by Sanity GROQ on our structured content.”

## 5. Admin & stack (30 s)

- Open **Admin**.
- Show **top cited sources** (from Sanity).
- Briefly mention stack: You.com for citations, Sanity for claim graph and compare, optional GPU worker on LKE.

## Talking points

- **You.com:** “We use the You.com API to get live, citation-backed search results.”
- **Sanity:** “Structured content in Sanity unlocks compare-by-topic, top sources, and future contradiction detection.”
- **Safety:** “We never run user input as shell commands; execute only returns generated artifacts.”
- **MCP:** “Schema and content operations were done through the Sanity MCP where applicable.”
