/**
 * ClaimGraphExplorer: renders claims with optional stance and citation links.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { ClaimGraphExplorer } from '../ClaimGraphExplorer';

const claims = [
  { id: 'cl-0', text: 'Claim one.', stance: 'neutral', citation_ids: [0] },
  { id: 'cl-1', text: 'Claim two.', stance: 'support', citation_ids: [1] },
];
const citations = [
  { title: 'Source 0', url: 'https://0.com', snippet: 'S0' },
  { title: 'Source 1', url: 'https://1.com', snippet: 'S1' },
];

describe('ClaimGraphExplorer', () => {
  it('renders nothing when claims is empty', () => {
    const { container } = render(<ClaimGraphExplorer claims={[]} citations={[]} />);
    expect(container.querySelector('section')).toBeNull();
  });

  it('renders heading and claim text', () => {
    render(<ClaimGraphExplorer claims={claims} citations={citations} />);
    expect(screen.getByText(/claim graph/i)).toBeInTheDocument();
    expect(screen.getByText('Claim one.')).toBeInTheDocument();
    expect(screen.getByText('Claim two.')).toBeInTheDocument();
  });

  it('renders stance badge for non-neutral', () => {
    render(<ClaimGraphExplorer claims={claims} citations={citations} />);
    expect(screen.getByText('support')).toBeInTheDocument();
  });

  it('renders citation links for claims', () => {
    render(<ClaimGraphExplorer claims={claims} citations={citations} />);
    const links = screen.getAllByRole('link');
    expect(links.some((l) => l.getAttribute('href') === 'https://0.com')).toBe(true);
    expect(links.some((l) => l.getAttribute('href') === 'https://1.com')).toBe(true);
  });
});
