// Shared types for LiveProof AI (used by web app; API keeps Python equivalents)

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
  stance?: 'support' | 'oppose' | 'neutral';
  citation_ids: string[];
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

export interface ExecuteRequest {
  session_id: string;
  action_type: 'code_snippet' | 'pdf_report' | 'config';
}

export interface ExecuteResponse {
  artifact: string; // base64 for PDF, raw text for code/config
  artifact_type: 'code' | 'pdf_base64' | 'config';
  logs: string[];
  safety_notes: string[];
}

export interface SessionSummary {
  id: string;
  topic?: string;
  question: string;
  reliability_score: number;
  created_at: string;
}

export interface TopicCompareItem {
  session_id: string;
  question: string;
  answer: string;
  reliability_score: number;
  created_at: string;
  claims_count: number;
}

export interface TopSource {
  url: string;
  title?: string;
  citation_count: number;
}

export const RELIABILITY_THRESHOLD = 0.65;
