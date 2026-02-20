/**
 * LiveProof AI – Sanity schema definitions.
 * Use with Sanity Studio or MCP (https://mcp.sanity.io) to create schema and seed content.
 * Structured content enables: compare sessions by topic, top sources, contradictions.
 */
import topic from './topic';
import session from './session';
import claim from './claim';
import source from './source';
import claimEdge from './claimEdge';

export const schemaTypes = [topic, session, claim, source, claimEdge];
