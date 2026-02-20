const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface VerifyInput {
  question: string;
  mode: 'answer' | 'execute';
  topic?: string;
}

export interface Citation {
  title: string;
  url: string;
  snippet: string;
  published_at?: string;
  source_name?: string;
}

export interface Claim {
  id: string;
  text: string;
  stance?: string;
  citation_ids: (string | number)[];
  confidence?: number;
}

export interface VerifyResponse {
  answer: string;
  reliability_score: number;
  claims: Claim[];
  citations: Citation[];
  session_id: string;
  can_execute: boolean;
  next_question?: string;
  topic?: string;
}

export interface ExecuteResponse {
  artifact: string;
  artifact_type: 'code' | 'pdf_base64' | 'config';
  logs: string[];
  safety_notes: string[];
}

export async function verify(body: VerifyInput): Promise<VerifyResponse> {
  const res = await fetch(`${API_BASE}/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function execute(sessionId: string, actionType: 'code_snippet' | 'pdf_report' | 'config'): Promise<ExecuteResponse> {
  const res = await fetch(`${API_BASE}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, action_type: actionType }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getSession(sessionId: string): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/session/${sessionId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export interface TopicCompareSession {
  session_id: string;
  question: string;
  answer: string;
  reliability_score: number;
  created_at?: string;
  claims_count: number;
}

export async function topicCompare(topic: string): Promise<{ topic: string; sessions: TopicCompareSession[] }> {
  const res = await fetch(`${API_BASE}/topic/${encodeURIComponent(topic)}/compare`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export interface TopSource {
  url: string;
  title?: string;
  citation_count: number;
}

export async function getTopSources(): Promise<{ sources: TopSource[] }> {
  const res = await fetch(`${API_BASE}/sources/top`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
