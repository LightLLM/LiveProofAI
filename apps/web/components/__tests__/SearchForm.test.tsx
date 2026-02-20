/**
 * SearchForm: render, submit calls onVerify with trimmed question/mode/topic.
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SearchForm } from '../SearchForm';

describe('SearchForm', () => {
  it('renders question textarea, mode select, topic input, and submit button', () => {
    const onVerify = jest.fn().mockResolvedValue(undefined);
    render(<SearchForm onVerify={onVerify} loading={false} />);
    expect(screen.getByLabelText(/question or task/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/mode/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/topic/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /verify & answer/i })).toBeInTheDocument();
  });

  it('submit is disabled when loading', () => {
    render(<SearchForm onVerify={jest.fn()} loading={true} />);
    expect(screen.getByRole('button', { name: /verifying/i })).toBeDisabled();
  });

  it('does not call onVerify when question is empty', async () => {
    const onVerify = jest.fn().mockResolvedValue(undefined);
    render(<SearchForm onVerify={onVerify} loading={false} />);
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => {});
    expect(onVerify).not.toHaveBeenCalled();
  });

  it('calls onVerify with question, mode, and topic on submit', async () => {
    const onVerify = jest.fn().mockResolvedValue(undefined);
    render(<SearchForm onVerify={onVerify} loading={false} />);
    fireEvent.change(screen.getByLabelText(/question or task/i), { target: { value: '  How does async work?  ' } });
    fireEvent.change(screen.getByLabelText(/mode/i), { target: { value: 'execute' } });
    fireEvent.change(screen.getByLabelText(/topic/i), { target: { value: 'python-asyncio' } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => expect(onVerify).toHaveBeenCalledTimes(1));
    expect(onVerify).toHaveBeenCalledWith('How does async work?', 'execute', 'python-asyncio');
  });

  it('passes undefined topic when topic field is empty', async () => {
    const onVerify = jest.fn().mockResolvedValue(undefined);
    render(<SearchForm onVerify={onVerify} loading={false} />);
    fireEvent.change(screen.getByLabelText(/question or task/i), { target: { value: 'Q' } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => expect(onVerify).toHaveBeenCalledWith('Q', 'answer', undefined));
  });
});
