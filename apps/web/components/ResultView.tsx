'use client';

import { useState } from 'react';
import type { VerifyResponse } from '@/lib/api';
import { EvidencePanel } from './EvidencePanel';
import { ClaimGraphExplorer } from './ClaimGraphExplorer';
import { execute } from '@/lib/api';

interface ResultViewProps {
  result: VerifyResponse;
}

export function ResultView({ result }: ResultViewProps) {
  const [executing, setExecuting] = useState(false);
  const [artifact, setArtifact] = useState<{ type: string; value: string } | null>(null);

  const handleExecute = async (actionType: 'code_snippet' | 'pdf_report' | 'config') => {
    setExecuting(true);
    setArtifact(null);
    try {
      const res = await execute(result.session_id, actionType);
      setArtifact({ type: res.artifact_type, value: res.artifact });
    } catch (e) {
      setArtifact({ type: 'error', value: e instanceof Error ? e.message : 'Execute failed' });
    } finally {
      setExecuting(false);
    }
  };

  const scorePercent = Math.round(result.reliability_score * 100);
  const scoreColor =
    result.reliability_score >= 0.65 ? 'text-[var(--accent)]' : 'text-amber-500';

  return (
    <div className="mt-8 space-y-6 border-t border-[var(--card)] pt-8">
      <section>
        <h2 className="text-lg font-semibold text-white mb-2">Answer</h2>
        <p className="text-[var(--muted)] leading-relaxed">{result.answer}</p>
      </section>

      <section className="flex flex-wrap items-center gap-4">
        <div>
          <span className="text-sm text-[var(--muted)]">Reliability score</span>
          <p className={`text-2xl font-bold ${scoreColor}`}>{scorePercent}%</p>
        </div>
        {result.can_execute ? (
          <p className="text-sm text-[var(--accent)]">Execution allowed (above threshold)</p>
        ) : (
          <p className="text-sm text-amber-500">
            Execution not allowed (below threshold). {result.next_question || ''}
          </p>
        )}
        {result.topic && (
          <p className="text-sm text-[var(--muted)]">Topic: {result.topic}</p>
        )}
      </section>

      {result.can_execute && (
        <section>
          <h3 className="text-sm font-medium text-[var(--muted)] mb-2">Execute</h3>
          <div className="flex gap-2">
            {(['code_snippet', 'pdf_report', 'config'] as const).map((action) => (
              <button
                key={action}
                onClick={() => handleExecute(action)}
                disabled={executing}
                className="px-4 py-2 rounded-lg bg-[var(--card)] border border-[var(--muted)]/30 text-white text-sm hover:border-[var(--accent)] disabled:opacity-50"
              >
                {action.replace('_', ' ')}
              </button>
            ))}
          </div>
          {artifact && (
            <div className="mt-4 p-4 rounded-lg bg-[var(--card)] border border-[var(--muted)]/30 overflow-auto max-h-80">
              {artifact.type === 'pdf_base64' ? (
                <a
                  href={`data:application/pdf;base64,${artifact.value}`}
                  download="liveproof-report.pdf"
                  className="text-[var(--accent)] underline"
                >
                  Download PDF report
                </a>
              ) : (
                <pre className="text-sm whitespace-pre-wrap font-mono text-[var(--muted)]">
                  {artifact.value}
                </pre>
              )}
            </div>
          )}
        </section>
      )}

      <EvidencePanel citations={result.citations} />
      <ClaimGraphExplorer claims={result.claims} citations={result.citations} />
    </div>
  );
}
