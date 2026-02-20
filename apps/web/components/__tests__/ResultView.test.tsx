/**
 * ResultView: shows answer, score, evidence, claim graph, execute buttons when can_execute.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { ResultView } from '../ResultView';

const result = {
  answer: 'The answer is async/await.',
  reliability_score: 0.75,
  claims: [{ id: 'cl-0', text: 'Claim', stance: 'neutral', citation_ids: [0] }],
  citations: [{ title: 'Doc', url: 'https://x.com', snippet: 'Snippet' }],
  session_id: 's1',
  can_execute: true,
  topic: 'python',
};

describe('ResultView', () => {
  it('renders answer and reliability score', () => {
    render(<ResultView result={result} />);
    expect(screen.getByText('The answer is async/await.')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('shows execution allowed when can_execute is true', () => {
    render(<ResultView result={result} />);
    expect(screen.getByText(/execution allowed/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /code snippet/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /pdf report/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^config$/i })).toBeInTheDocument();
  });

  it('does not show execute buttons when can_execute is false', () => {
    render(<ResultView result={{ ...result, can_execute: false }} />);
    expect(screen.queryByRole('button', { name: /code snippet/i })).not.toBeInTheDocument();
  });

  it('renders evidence and claim graph sections', () => {
    render(<ResultView result={result} />);
    expect(screen.getByText(/evidence \(citations\)/i)).toBeInTheDocument();
    expect(screen.getByText(/claim graph/i)).toBeInTheDocument();
  });
});
