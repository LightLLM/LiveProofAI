/**
 * EvidencePanel: renders list of citations with links and snippets.
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { EvidencePanel } from '../EvidencePanel';

const citations = [
  { title: 'Doc A', url: 'https://a.com', snippet: 'Snippet A', source_name: 'Source A' },
  { title: 'Doc B', url: 'https://b.com', snippet: 'Snippet B' },
];

describe('EvidencePanel', () => {
  it('renders nothing when citations is empty', () => {
    const { container } = render(<EvidencePanel citations={[]} />);
    expect(container.querySelector('section')).toBeNull();
  });

  it('renders section heading and citation links', () => {
    render(<EvidencePanel citations={citations} />);
    expect(screen.getByText(/evidence \(citations\)/i)).toBeInTheDocument();
    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(2);
    expect(links[0]).toHaveAttribute('href', 'https://a.com');
    expect(links[0]).toHaveTextContent('Doc A');
    expect(links[1]).toHaveAttribute('href', 'https://b.com');
    expect(links[1]).toHaveTextContent('Doc B');
  });

  it('renders snippets', () => {
    render(<EvidencePanel citations={citations} />);
    expect(screen.getByText('Snippet A')).toBeInTheDocument();
    expect(screen.getByText('Snippet B')).toBeInTheDocument();
  });
});
