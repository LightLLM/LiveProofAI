/**
 * API client tests with mocked fetch.
 */
import {
  verify,
  execute,
  getSession,
  topicCompare,
  getTopSources,
} from '../api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

beforeEach(() => {
  global.fetch = jest.fn();
});

function mockResolve(json: unknown, ok = true) {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok,
    text: () => Promise.resolve(JSON.stringify(json)),
    json: () => Promise.resolve(json),
  });
}

function mockReject(status: number, detail: string) {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: false,
    text: () => Promise.resolve(detail),
  });
}

describe('verify', () => {
  it('calls POST /verify and returns response', async () => {
    const body = { answer: 'Yes', reliability_score: 0.8, claims: [], citations: [], session_id: 's1', can_execute: false };
    mockResolve(body);
    const result = await verify({ question: 'Test?', mode: 'answer' });
    expect(result).toEqual(body);
    expect(fetch).toHaveBeenCalledWith(
      `${API_BASE}/verify`,
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: 'Test?', mode: 'answer' }),
      })
    );
  });

  it('includes topic when provided', async () => {
    mockResolve({ session_id: 's1', answer: '', reliability_score: 0, claims: [], citations: [], can_execute: false });
    await verify({ question: 'Q', mode: 'answer', topic: 'python' });
    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        body: JSON.stringify({ question: 'Q', mode: 'answer', topic: 'python' }),
      })
    );
  });

  it('throws on non-ok response', async () => {
    mockReject(500, 'Server error');
    await expect(verify({ question: 'Q', mode: 'answer' })).rejects.toThrow();
  });
});

describe('execute', () => {
  it('calls POST /execute with session_id and action_type', async () => {
    const body = { artifact: 'code', artifact_type: 'code', logs: [], safety_notes: [] };
    mockResolve(body);
    const result = await execute('session-1', 'code_snippet');
    expect(result.artifact_type).toBe('code');
    expect(fetch).toHaveBeenCalledWith(
      `${API_BASE}/execute`,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ session_id: 'session-1', action_type: 'code_snippet' }),
      })
    );
  });
});

describe('getSession', () => {
  it('calls GET /session/:id', async () => {
    const body = { session_id: 's1', question: 'Q', answer: 'A' };
    mockResolve(body);
    const result = await getSession('s1');
    expect(result.session_id).toBe('s1');
    expect(fetch).toHaveBeenCalledWith(`${API_BASE}/session/s1`);
  });
});

describe('topicCompare', () => {
  it('calls GET /topic/:topic/compare and returns topic and sessions', async () => {
    const body = { topic: 'python-asyncio', sessions: [] };
    mockResolve(body);
    const result = await topicCompare('python-asyncio');
    expect(result.topic).toBe('python-asyncio');
    expect(result.sessions).toEqual([]);
    expect(fetch).toHaveBeenCalledWith(`${API_BASE}/topic/python-asyncio/compare`);
  });

  it('encodes topic in URL', async () => {
    mockResolve({ topic: 'a b', sessions: [] });
    await topicCompare('a b');
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining(encodeURIComponent('a b')));
  });
});

describe('getTopSources', () => {
  it('calls GET /sources/top and returns sources', async () => {
    const body = { sources: [{ url: 'https://x.com', citation_count: 1 }] };
    mockResolve(body);
    const result = await getTopSources();
    expect(result.sources).toHaveLength(1);
    expect(result.sources[0].url).toBe('https://x.com');
    expect(fetch).toHaveBeenCalledWith(`${API_BASE}/sources/top`);
  });
});
