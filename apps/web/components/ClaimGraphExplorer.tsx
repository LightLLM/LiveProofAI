'use client';

import type { Claim, Citation } from '@/lib/api';

interface ClaimGraphExplorerProps {
  claims: Claim[];
  citations: Citation[];
}

export function ClaimGraphExplorer({ claims, citations }: ClaimGraphExplorerProps) {
  if (!claims?.length) return null;

  const getCitation = (id: string | number) => {
    const idx = typeof id === 'number' ? id : citations.findIndex((_, i) => i === id);
    return citations[idx];
  };

  return (
    <section>
      <h2 className="text-lg font-semibold text-white mb-3">Claim Graph</h2>
      <p className="text-sm text-[var(--muted)] mb-4">
        Claims derived from evidence; each claim links to one or more sources.
      </p>
      <ul className="space-y-4">
        {claims.map((claim) => (
          <li
            key={claim.id}
            className="p-4 rounded-lg bg-[var(--card)] border border-[var(--muted)]/20"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-mono text-[var(--accent)]">{claim.id}</span>
              {claim.stance && claim.stance !== 'neutral' && (
                <span className="text-xs px-2 py-0.5 rounded bg-[var(--muted)]/30">
                  {claim.stance}
                </span>
              )}
            </div>
            <p className="text-[var(--muted)] text-sm">{claim.text}</p>
            {claim.citation_ids?.length > 0 && (
              <ul className="mt-2 space-y-1">
                {claim.citation_ids.map((cid, j) => {
                  const c = getCitation(cid);
                  if (!c) return null;
                  return (
                    <li key={j}>
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-[var(--accent)] hover:underline"
                      >
                        {c.title || c.url}
                      </a>
                    </li>
                  );
                })}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
