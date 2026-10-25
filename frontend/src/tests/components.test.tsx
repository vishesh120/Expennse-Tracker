// @vitest-environment jsdom
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { StatCard } from '../components/StatCard';
import { EmptyState } from '../components/EmptyState';
import { Wallet, Receipt } from 'lucide-react';

describe('Frontend UI Components', () => {
  it('renders StatCard with title, amount and subtitle', () => {
    render(
      <StatCard
        title="Total Income"
        amount="₹65,000"
        subtitle="Earned this month"
        icon={Wallet}
        change={12.5}
      />
    );

    expect(screen.getByText('Total Income')).toBeDefined();
    expect(screen.getByText('₹65,000')).toBeDefined();
    expect(screen.getByText('Earned this month')).toBeDefined();
    expect(screen.getByText('+12.5%')).toBeDefined();
  });

  it('renders EmptyState with custom title, message and CTA button', () => {
    let clicked = false;
    render(
      <EmptyState
        icon={Receipt}
        title="No Transactions"
        description="Add your first payment now."
        actionText="Add Transaction"
        onAction={() => { clicked = true; }}
      />
    );

    expect(screen.getByText('No Transactions')).toBeDefined();
    expect(screen.getByText('Add your first payment now.')).toBeDefined();
    const btn = screen.getByText('Add Transaction');
    expect(btn).toBeDefined();
    btn.click();
    expect(clicked).toBe(true);
  });
});
