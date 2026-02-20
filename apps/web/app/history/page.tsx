'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { topicCompare, type TopicCompareSession } from '@/lib/api';

export default function HistoryPage() {
  const [topic, setTopic] = useState('python-asyncio');
  const [sessions, setSessions] = useState<TopicCompareSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCompare = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await topicCompare(topic);
      setSessions(res.sessions || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load');
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompare();
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-[var(--card)] bg-[var(--card)]/50 backdrop-blur">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-semibold text-[var(--accent)]">
            LiveProof AI
          </Link>
          <nav className="flex gap-4 text-sm text-[var(--muted)]">
            <Link href="/" className="hover:text-white">Home</Link>
            <Link href="/admin" className="hover:text-white">Admin</Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-white mb-2">Compare by topic</h1>
        <p className="text-[var(--muted)] mb-6">
          Sessions for the same topic (from Sanity). Compare answers over time.
        </p>

        <div className="flex gap-2 mb-6">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Topic slug (e.g. python-asyncio)"
            className="flex-1 px-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--muted)]/30 text-white placeholder-[var(--muted)]"
          />
          <button
            onClick={fetchCompare}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-[var(--accent)] text-[var(--bg)] font-medium disabled:opacity-50"
          >
            {loading ? 'Loading…' : 'Compare'}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 rounded-lg bg-[var(--danger)]/20 text-[var(--danger)]">
            {error}
          </div>
        )}

        {sessions.length === 0 && !loading && (
          <p className="text-[var(--muted)]">
            No sessions for this topic yet. Run a verify with the same topic on the home page.
          </p>
        )}

        <ul className="space-y-4">
          {sessions.map((s) => (
            <li
              key={s.session_id}
              className="p-4 rounded-lg bg-[var(--card)] border border-[var(--muted)]/20"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-[var(--accent)]">{s.session_id.slice(0, 8)}…</span>
                <span className="text-sm text-[var(--muted)]">
                  Score: {Math.round((s.reliability_score ?? 0) * 100)}% · {s.claims_count ?? 0} claims
                </span>
              </div>
              <p className="text-white font-medium mb-1">{s.question}</p>
              <p className="text-sm text-[var(--muted)] line-clamp-2">{s.answer}</p>
              {s.created_at && (
                <p className="text-xs text-[var(--muted)] mt-2">{s.created_at}</p>
              )}
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
