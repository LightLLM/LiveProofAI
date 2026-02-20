# Sanity MCP – LiveProof AI

Connect Cursor/Claude to Sanity via **https://mcp.sanity.io** to manage schema and run GROQ during development.

## Setup

1. In Cursor MCP settings, add a server that points to `https://mcp.sanity.io`.
2. Provide your Sanity project ID and dataset (and token if you need write access from MCP).

## Schema and content (MCP)

- **Schema**: The types `topic`, `session`, `claim`, `source`, `claimEdge` are defined in `sanity/schemas/`. Use MCP tools to create or update schema in your Sanity project to match these.
- **Seed content**: Use MCP document create/patch to seed sample topics, sessions, claims, and sources.
- **GROQ during development**: Use MCP run GROQ for:
  - Compare sessions by topic
  - Top sources
  - Contradictions (claims with stance support/oppose for same topic)

## GROQ examples

```groq
// Sessions for topic (compare view)
*[_type == "session" && topic->slug == "python-asyncio"] | order(createdAt desc) {
  _id, question, answer, reliabilityScore, createdAt,
  "claims_count": count(claims)
}

// Top cited sources
*[_type == "source"] {
  _id, url, title,
  "citation_count": count(*[_type == "claim" && references(^._id)])
} | order(citation_count desc) [0...20]

// Contradictions: claims with opposing stance per topic
*[_type == "claim" && stance != "neutral"] {
  _id, text, stance, topic->{ slug }, "session_id": session._ref
}
```

In the submission we call out that schema and content operations were done through the Sanity MCP.
