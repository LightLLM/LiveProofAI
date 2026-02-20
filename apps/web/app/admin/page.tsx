'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getTopSources } from '@/lib/api';

export default function AdminPage() {
  const [sources, setSources] = useState<{ url: string; title?: string; citation_count: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTopSources()
      .then((res) => setSources(res.sources || []))
      .catch(() => setSources([]))
      .finally(() => setLoading(false));
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
            <Link href="/history" className="hover:text-white">History</Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-white mb-2">Admin / Dev</h1>
        <p className="text-[var(--muted)] mb-6">
          Raw data: top cited sources (from Sanity GROQ). You.com responses and Sanity mutations are visible in API logs.
        </p>

        <section className="mb-8">
          <h2 className="text-lg font-semibold text-white mb-3">Top cited sources (GROQ)</h2>
          {loading ? (
            <p className="text-[var(--muted)]">Loading…</p>
          ) : sources.length === 0 ? (
            <p className="text-[var(--muted)]">No sources yet or Sanity not configured.</p>
          ) : (
            <ul className="space-y-2">
              {sources.map((s, i) => (
                <li key={i} className="flex items-center gap-4 text-sm">
                  <span className="text-[var(--accent)] w-8">{s.citation_count}</span>
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[var(--accent)] hover:underline truncate flex-1"
                  >
                    {s.title || s.url}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="p-4 rounded-lg bg-[var(--card)] border border-[var(--muted)]/20 font-mono text-xs text-[var(--muted)]">
          <p className="font-semibold text-white mb-2">GROQ used for compare:</p>
          <pre className="whitespace-pre-wrap break-all">
            {`*[_type == "session" && topic->slug == $slug] | order(createdAt desc) {
  _id, question, answer, reliabilityScore, createdAt,
  "claims_count": count(claims)
}`}
          </pre>
          <p className="font-semibold text-white mt-4 mb-2">GROQ for top sources:</p>
          <pre className="whitespace-pre-wrap break-all">
            {`*[_type == "source"] {
  _id, url, title,
  "citation_count": count(*[_type == "claim" && references(^._id)])
} | order(citation_count desc) [0...$limit]`}
          </pre>
        </section>
      </main>
    </div>
  );
}
