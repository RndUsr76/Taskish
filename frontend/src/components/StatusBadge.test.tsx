import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  it('renders TODO status correctly', () => {
    render(<StatusBadge status="TODO" />);
    expect(screen.getByText('To Do')).toBeInTheDocument();
  });

  it('renders IN_PROGRESS status correctly', () => {
    render(<StatusBadge status="IN_PROGRESS" />);
    expect(screen.getByText('In Progress')).toBeInTheDocument();
  });

  it('renders BLOCKED status correctly', () => {
    render(<StatusBadge status="BLOCKED" />);
    expect(screen.getByText('Blocked')).toBeInTheDocument();
  });

  it('renders DONE status correctly', () => {
    render(<StatusBadge status="DONE" />);
    expect(screen.getByText('Done')).toBeInTheDocument();
  });

  it('applies correct color class for TODO', () => {
    render(<StatusBadge status="TODO" />);
    const badge = screen.getByText('To Do');
    expect(badge).toHaveClass('bg-gray-100', 'text-gray-800');
  });

  it('applies correct color class for IN_PROGRESS', () => {
    render(<StatusBadge status="IN_PROGRESS" />);
    const badge = screen.getByText('In Progress');
    expect(badge).toHaveClass('bg-blue-100', 'text-blue-800');
  });

  it('applies correct color class for BLOCKED', () => {
    render(<StatusBadge status="BLOCKED" />);
    const badge = screen.getByText('Blocked');
    expect(badge).toHaveClass('bg-red-100', 'text-red-800');
  });

  it('applies correct color class for DONE', () => {
    render(<StatusBadge status="DONE" />);
    const badge = screen.getByText('Done');
    expect(badge).toHaveClass('bg-green-100', 'text-green-800');
  });
});
