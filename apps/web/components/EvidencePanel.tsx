'use client';

import type { Citation } from '@/lib/api';

interface EvidencePanelProps {
  citations: Citation[];
}

export function EvidencePanel({ citations }: EvidencePanelProps) {
  if (!citations?.length) return null;

  return (
    <section>
      <h2 className="text-lg font-semibold text-white mb-3">Evidence (citations)</h2>
      <ul className="space-y-3">
        {citations.map((c, i) => (
          <li
            key={i}
            className="p-4 rounded-lg bg-[var(--card)] border border-[var(--muted)]/20"
          >
            <a
              href={c.url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-[var(--accent)] hover:underline block mb-1"
            >
              {c.title || c.url}
            </a>
            {c.source_name && (
              <span className="text-xs text-[var(--muted)]">{c.source_name}</span>
            )}
            <p className="text-sm text-[var(--muted)] mt-1 line-clamp-2">{c.snippet}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
