'use client';

import { useState } from 'react';

type Mode = 'answer' | 'execute';

interface SearchFormProps {
  onVerify: (question: string, mode: Mode, topic?: string) => Promise<void>;
  loading: boolean;
}

export function SearchForm({ onVerify, loading }: SearchFormProps) {
  const [question, setQuestion] = useState('');
  const [mode, setMode] = useState<Mode>('answer');
  const [topic, setTopic] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    await onVerify(question.trim(), mode, topic.trim() || undefined);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="question" className="block text-sm font-medium text-[var(--muted)] mb-1">
          Question or task
        </label>
        <textarea
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. How do I use async/await in Python with FastAPI?"
          rows={3}
          className="w-full px-4 py-3 rounded-lg bg-[var(--card)] border border-[var(--muted)]/30 text-white placeholder-[var(--muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
          disabled={loading}
        />
      </div>
      <div className="flex flex-wrap gap-4 items-center">
        <div>
          <label className="block text-sm font-medium text-[var(--muted)] mb-1">Mode</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as Mode)}
            className="px-3 py-2 rounded-lg bg-[var(--card)] border border-[var(--muted)]/30 text-white focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
            disabled={loading}
          >
            <option value="answer">Answer only</option>
            <option value="execute">Answer + allow execute (code/PDF/config)</option>
          </select>
        </div>
        <div className="flex-1 min-w-[200px]">
          <label htmlFor="topic" className="block text-sm font-medium text-[var(--muted)] mb-1">
            Topic (optional, for compare)
          </label>
          <input
            id="topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. python-asyncio"
            className="w-full px-3 py-2 rounded-lg bg-[var(--card)] border border-[var(--muted)]/30 text-white placeholder-[var(--muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
            disabled={loading}
          />
        </div>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="px-6 py-3 rounded-lg bg-[var(--accent)] text-[var(--bg)] font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Verifying…' : 'Verify & Answer'}
      </button>
    </form>
  );
}
