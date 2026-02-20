'use client';

import { useState } from 'react';
import Link from 'next/link';
import { SearchForm } from '@/components/SearchForm';
import { ResultView } from '@/components/ResultView';
import type { VerifyResponse } from '@/lib/api';

export default function Home() {
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async (question: string, mode: 'answer' | 'execute', topic?: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/verify`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, mode, topic }),
        }
      );
      if (!res.ok) throw new Error(await res.text());
      const data: VerifyResponse = await res.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-[var(--card)] bg-[var(--card)]/50 backdrop-blur">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-semibold text-[var(--accent)]">
            LiveProof AI
          </Link>
          <nav className="flex gap-4 text-sm text-[var(--muted)]">
            <Link href="/history" className="hover:text-white">History</Link>
            <Link href="/admin" className="hover:text-white">Admin</Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Verify & Answer
          </h1>
          <p className="text-[var(--muted)]">
            Ask a technical question. We fetch live evidence, build a claim graph, and only act when reliability is high.
          </p>
        </div>

        <SearchForm onVerify={handleVerify} loading={loading} />

        {error && (
          <div className="mt-4 p-4 rounded-lg bg-[var(--danger)]/20 text-[var(--danger)]">
            {error}
          </div>
        )}

        {result && <ResultView result={result} />}
      </main>
    </div>
  );
}
